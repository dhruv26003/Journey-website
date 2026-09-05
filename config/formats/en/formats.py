# Custom date formats for en locale in Django
DATE_INPUT_FORMATS = [
    '%d/%m/%Y',      # '16/06/2026', '16/6/2026'
    '%d-%m-%Y',      # '16-06-2026', '16-6-2026'
    '%Y-%m-%d',      # '2026-06-16'
    '%m/%d/%Y',      # '06/16/2026'
    '%d/%m/%y',      # '16/6/26'
    '%d-%m-%y',      # '16-6-26'
    '%Y/%m/%d',      # '2026/06/16'
    '%b %d, %Y',     # 'Jun 16, 2026'
    '%b. %d, %Y',    # 'Jun. 16, 2026'
    '%d %B %Y',      # '16 June 2026'
    '%B %d, %Y',     # 'June 16, 2026'
]

DATE_FORMAT = 'd/m/Y'
SHORT_DATE_FORMAT = 'd/m/Y'
