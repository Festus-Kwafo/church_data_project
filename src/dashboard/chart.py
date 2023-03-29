months = [
    'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]

colorPalette = ['rgba(255, 99, 132, 0.2)', '#81ecec', '#a29bfe', '#ffeaa7', '#fab1a0', '#ff7675', '#fd79a8']
colorPrimary, colorSuccess, colorDanger = '#366FB6', colorPalette[0], colorPalette[5]

def get_year_dict():
    year_dict = dict()

    for month in months:
        year_dict[month] = 0

    return year_dict
