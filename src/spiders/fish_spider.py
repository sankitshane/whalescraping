import scrapy

class plantsdata(scrapy.Spider):
    name = "plants"

    start_urls = [
        'https://tropica.com/en/plants/'
    ]

    def parse(self, response):
        for cat in response.css('div.plant-item'):
            link = cat.css('a::attr(href)').get()
            #print(link) 
            CategoryName = cat.css('strong::text').get()
            #print(CategoryName)
            ShortDescription = cat.css('li::text').getall()
            #print(ShortDescription) 

            data = {
                "Category" : CategoryName,
                "SDesc" : ShortDescription
            } 

            if link is not None:
                yield response.follow(link, callback=self.SubParse, cb_kwargs=dict(parentaldata=data))

    def SubParse(self, response, parentaldata):
        Desc = response.css('div.description').css('p::text').getall()
        Description = ''

        for data in Desc:
            Description += data.strip()
        
        statsdata = response.css('table.specficationTable').css('tr')
        stats = {}

        for st in statsdata:
            try:
                stats[st.css('th::text').get().strip()[:-1].strip()] = st.css('td::text').get().strip()
            except:
                pass
        
        difficulty = response.css('div.difficulty').css('img::attr(src)').get()[30:-4]


        yield {
            'Category' : parentaldata['Category'],
            'ShortDesc' : parentaldata['SDesc'],
            'Stats': stats,
            'Desc' : Description,
            'Difficulty': difficulty
        }

        


class FishSpider(scrapy.Spider):
    name = "Fish"

    start_urls  = [
        'https://www.liveaquaria.com/category/830/freshwater-fish',
        'https://www.liveaquaria.com/category/15/marine-fish',
        'https://www.liveaquaria.com/category/497/marine-invert-plant',
        'https://www.liveaquaria.com/category/1075/freshwater-inverts',
    ]

    def parse(self, response):
        for cat in response.css('a.cat-name'):
            categoryText = cat.css('a::text').get().strip()
            categoryLink = cat.css('a::attr(href)').get()
            #print("Category: {}, Link {}".format(categoryText, categoryLink))

            data = {
                "Category": categoryText
            }

            if categoryLink is not None:
                yield response.follow(categoryLink, callback=self.parseTags, cb_kwargs=dict(parentalData=data))


    def parseTags(self, response, parentalData):
        for cat in response.css('a.cat-name'):
            fishName = cat.css('a::text').get().strip()
            fishInfoLinks = cat.css('a::attr(href)').get()
            #print("Fish Name: {} and Fish Link {}".format(fishName, fishInfoLinks))
            
            data = {
                'Category': parentalData['Category'],
                "FishName": fishName,
            }

            if fishInfoLinks is not None:
                yield response.follow(fishInfoLinks, callback=self.parseInfo, cb_kwargs=dict(productBasic=data))
        
    
    def parseInfo(self, response, productBasic):
        fishsciname = response.css('span.prodScientificName::text').get()

        if fishsciname is not None:
            fishsciname = fishsciname.strip()[1:-1]

        productBasic['ScintificName'] = fishsciname

        overview = response.css('div.overview-content::text').get().strip()

        for view in response.css('div.overview-content').css('p::text').getall()[:-1]:
            overview += view.strip()

        result = {'Overview': overview, 'stats':{}, **productBasic}
        
        for cat in response.css('div.quick_stat_entry'):
            label = cat.css('span.quick_stat_label').css('a::text').get()
            value = cat.css('span.quick_stat_value::text').get()

            if label is not None and value is not None and label.strip() != 'Compatibility':
                result['stats'][label.strip()] = value.strip()

        yield result