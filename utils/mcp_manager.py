import asyncio
import json
import logging
import httpx

class YokTezMCPManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.url = "https://yoktezmcp.fastmcp.app/mcp/"

    async def _fetch_single(self, query: str, search_type: str, client: httpx.AsyncClient) -> list:
        results = []
        try:
            args = {"results_per_page": 20}
            
            if search_type == "Yazar Adı":
                tr_query = query.replace('i', 'İ').replace('ı', 'I').upper()
                args["author_name"] = tr_query
            elif search_type == "Danışman Adı":
                tr_query = query.replace('i', 'İ').replace('ı', 'I').upper()
                args["advisor_name"] = tr_query
            else:
                args["thesis_title"] = query
                
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search_yok_tez_detailed",
                    "arguments": args
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            self.logger.info(f"Sending POST to FastMCP ({search_type}): {payload}")
            resp = await client.post(self.url, json=payload, headers=headers)
            
            for line in resp.text.splitlines():
                if line.startswith('data: '):
                    data_str = line[6:].strip()
                    if not data_str: continue
                    
                    try:
                        response_json = json.loads(data_str)
                        if response_json.get("error"):
                            self.logger.error(f"MCP API Error: {response_json['error']}")
                            continue
                            
                        tool_result = response_json.get("result", {})
                        if tool_result.get("isError"):
                            self.logger.error(f"MCP Tool returned error: {tool_result}")
                            continue
                            
                        content_list = tool_result.get("content", [])
                        if content_list and isinstance(content_list, list) and len(content_list) > 0:
                            data_text = content_list[0].get("text", "")
                            
                            try:
                                data_dict = json.loads(data_text)
                                theses = data_dict.get("theses", [])
                                self.logger.info(f"Parsed {len(theses)} theses successfully for {search_type}.")
                                
                                for thesis in theses:
                                    yazar_ad_soyad = thesis.get("author", "Bilinmiyor")
                                    danisman = thesis.get("advisor", "")
                                    
                                    # Fallback strict match for title
                                    if search_type not in ["Yazar Adı", "Danışman Adı"]:
                                        query_lower = query.lower().replace('i̇', 'i').replace('ı', 'i')
                                        title_lower = thesis.get("title", "").lower().replace('i̇', 'i').replace('ı', 'i')
                                        if query_lower not in title_lower:
                                            continue
                                            
                                    # Advisor formatting
                                    if danisman:
                                        advisor_str = f"Danışman: {danisman} - {thesis.get('university_info', 'Bilinmiyor')}"
                                    else:
                                        advisor_str = thesis.get('university_info', 'Bilinmiyor')
                                        
                                    author_field = f"{yazar_ad_soyad} ({advisor_str})"
                                    if search_type == "Danışman Adı":
                                        author_field = f"[Rol: Danışman - Aranan: {query}] {author_field}"
                                        
                                    results.append({
                                        "Kaynak": "YÖK Tez (Remote MCP)",
                                        "Yıl": str(thesis.get("year", "Bilinmiyor")),
                                        "Başlık": thesis.get("title", "Bilinmiyor"),
                                        "Yazarlar": author_field,
                                        "Erişim Durumu": "Açık",
                                        "DOI": "-",
                                        "Link": thesis.get("detail_page_url", ""),
                                        "Özet": thesis.get("abstract", "Özet içeriği çekilmedi.")
                                    })
                            except json.JSONDecodeError as decode_err:
                                self.logger.error(f"Failed to parse inner data_text as JSON: {data_text[:200]}... Error: {decode_err}")
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse inner data block loop: {str(e)}")
        except Exception as e:
            self.logger.error(f"Single fetch hatası ({search_type}): {str(e)}")
            
        return results

    async def fetch(self, query: str, search_type: str = "Kavram/Kelime Arama") -> dict:
        merged_results = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if search_type == "Yazar Adı":
                    # Fire both author and advisor queries concurrently
                    author_coro = self._fetch_single(query, "Yazar Adı", client)
                    advisor_coro = self._fetch_single(query, "Danışman Adı", client)
                    
                    author_res, advisor_res = await asyncio.gather(author_coro, advisor_coro)
                    merged_results.extend(author_res)
                    merged_results.extend(advisor_res)
                else:
                    # Document Title / Keyword queries only fire once
                    merged_results = await self._fetch_single(query, search_type, client)
                    
            # Deduplicate by Link
            seen_links = set()
            unique_results = []
            for item in merged_results:
                link = item.get("Link")
                if link and link not in seen_links:
                    seen_links.add(link)
                    unique_results.append(item)
                elif not link:
                    unique_results.append(item)
                        
            return {
                "source": "YÖK Tez (Remote)",
                "status": "success",
                "message": "",
                "data": unique_results
            }
        except Exception as e:
            self.logger.error(f"Remote MCP YÖK Tez hatası: {str(e)}")
            return {
                "source": "YÖK Tez (Remote)",
                "status": "error",
                "message": f"Remote MCP sunucusuna bağlanılamadı: {str(e)}",
                "data": []
            }
