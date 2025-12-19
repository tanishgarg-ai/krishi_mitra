# import requests
# from datetime import datetime
# from bs4 import BeautifulSoup
#
#
# def get_paddy_prices(state=None, district=None, market=None, date_offset=0):
#     """
#     Get current paddy prices from AGMARKNET
#
#     Args:
#         state (str): State name (e.g., 'Punjab', 'Haryana')
#         district (str): District name (e.g., 'Ludhiana', 'Karnal')
#         market (str): Specific market name
#         date_offset (int): Days back from today (0 = today)
#
#     Returns:
#         dict: Price data or error message
#     """
#
#     # Paddy commodity code in AGMARKNET
#     PADDY_COMMODITY_CODE = "30"
#
#     # Calculate target date
#     target_date = datetime.now()
#     if date_offset > 0:
#         from datetime import timedelta
#         target_date = target_date - timedelta(days=date_offset)
#
#     date_str = target_date.strftime("%d/%m/%Y")
#
#     # Prepare payload
#     payload = {
#         'opt': 'com',
#         'state': state or '',
#         'district': district or '',
#         'market': market or '',
#         'commodity': PADDY_COMMODITY_CODE,
#         'fromdate': date_str,
#         'todate': date_str,
#         'type': 'price'
#     }
#
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Referer': 'https://agmarknet.gov.in/',
#         'Origin': 'https://agmarknet.gov.in'
#     }
#
#     try:
#         response = requests.post(
#             'https://agmarknet.gov.in/agnew/CommonController?actionname=PriceArrivalsInfo',
#             data=payload,
#             headers=headers,
#             timeout=15
#         )
#         print(response.text)
#         response.raise_for_status()
#
#         return parse_paddy_prices(response.text, state, district)
#
#     except requests.exceptions.RequestException as e:
#         return {
#             'success': False,
#             'error': f"Network error: {str(e)}",
#             'data': []
#         }
#     except Exception as e:
#         return {
#             'success': False,
#             'error': f"Processing error: {str(e)}",
#             'data': []
#         }
#
#
# def parse_paddy_prices(html_content, state_filter=None, district_filter=None):
#     """
#     Parse the HTML response and extract paddy price data
#     """
#     soup = BeautifulSoup(html_content, 'html.parser')
#
#     # Find the price table
#     table = soup.find('table', {'class': 'table-striped'})
#
#     if not table:
#         return {
#             'success': False,
#             'error': 'No price data found for the given parameters',
#             'data': []
#         }
#
#     prices = []
#     rows = table.find_all('tr')[1:]  # Skip header row
#
#     for row in rows:
#         cols = row.find_all('td')
#
#         # Expected columns: State, District, Market, Commodity, Variety, Grade, Min Price, Max Price, Modal Price
#         if len(cols) >= 8:
#             price_data = {
#                 'state': cols[0].get_text(strip=True),
#                 'district': cols[1].get_text(strip=True),
#                 'market': cols[2].get_text(strip=True),
#                 'commodity': cols[3].get_text(strip=True),
#                 'variety': cols[4].get_text(strip=True) if len(cols) > 4 else 'N/A',
#                 'grade': cols[5].get_text(strip=True) if len(cols) > 5 else 'N/A',
#                 'min_price': cols[6].get_text(strip=True) + ' ₹/quintal',
#                 'max_price': cols[7].get_text(strip=True) + ' ₹/quintal',
#                 'modal_price': cols[8].get_text(strip=True) + ' ₹/quintal' if len(cols) > 8 else 'N/A',
#                 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#
#             # Apply filters if provided
#             if state_filter and state_filter.lower() not in price_data['state'].lower():
#                 continue
#             if district_filter and district_filter.lower() not in price_data['district'].lower():
#                 continue
#
#             prices.append(price_data)
#
#     return {
#         'success': True,
#         'count': len(prices),
#         'data': prices,
#         'query_time': datetime.now().isoformat()
#     }
#
#
# def format_paddy_prices_for_display(price_data, lang='en'):
#     """
#     Format the price data for user display
#     """
#     if not price_data['success'] or price_data['count'] == 0:
#         if lang == 'hi':
#             return "क्षमा करें, आज के लिए धान की कीमतें उपलब्ध नहीं हैं। कृपया कल फिर कोशिश करें।"
#         else:
#             return "Sorry, paddy prices are not available for today. Please try again tomorrow."
#
#     results = price_data['data']
#
#     if lang == 'hi':
#         response = f"🌾 **धान की कीमतें** ({len(results)} बाजार)\n\n"
#         for price in results[:5]:  # Show top 5 results
#             response += f"📍 **{price['market']}, {price['district']}**\n"
#             response += f"   • न्यूनतम: {price['min_price']}\n"
#             response += f"   • अधिकतम: {price['max_price']}\n"
#             if price['modal_price'] != 'N/A':
#                 response += f"   • औसत: {price['modal_price']}\n"
#             response += f"   • किस्म: {price['variety']}\n\n"
#
#     else:
#         response = f"🌾 **Paddy Prices** ({len(results)} markets)\n\n"
#         for price in results[:5]:  # Show top 5 results
#             response += f"📍 **{price['market']}, {price['district']}**\n"
#             response += f"   • Min: {price['min_price']}\n"
#             response += f"   • Max: {price['max_price']}\n"
#             if price['modal_price'] != 'N/A':
#                 response += f"   • Avg: {price['modal_price']}\n"
#             response += f"   • Variety: {price['variety']}\n\n"
#
#     if len(results) > 5:
#         if lang == 'hi':
#             response += f"... और {len(results) - 5} और बाजार"
#         else:
#             response += f"... and {len(results) - 5} more markets"
#
#     return response
#
#
# if __name__ == '__main__':
#     # Example 1: Get all paddy prices across India
#     all_prices = get_paddy_prices()
#     print(format_paddy_prices_for_display(all_prices))
#
#     # Example 2: Get paddy prices for Punjab state
#     punjab_prices = get_paddy_prices(state="Punjab")
#     print(format_paddy_prices_for_display(punjab_prices))
#
#     # Example 3: Get paddy prices for specific district
#     karnal_prices = get_paddy_prices(state="Haryana", district="Karnal")
#     print(format_paddy_prices_for_display(karnal_prices))
#
#     # Example 4: In Hindi
#     hindi_prices = format_paddy_prices_for_display(punjab_prices, lang='hi')
#     print(hindi_prices)
#
#     # Example 5: Yesterday's prices (if available)
#     yesterday_prices = get_paddy_prices(date_offset=1)




for i in range(500):
    print(1,end='')
print(0,end='')
for i in range(500):
    print(1,end='')
print(0, end='')
for i in range(500):
    print(1,end='')
print(0,end='')
for i in range(500):
    print(1,end='')
print(0, end='')
for i in range(500):
    print(1,end='')
print(0,end='')
for i in range(500):
    print(1,end='')
print(0, end='')
for i in range(500):
    print(1,end='')
print(0,end='')
for i in range(500):
    print(1,end='')
print(0, end='')
