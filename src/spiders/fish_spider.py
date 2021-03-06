import scrapy

class fishAquaHobby(scrapy.Spider):
    name = 'fishAquahobby'

    start_urls = [
        'http://www.aquahobby.com/e_freshwater_tropical_aquarium_fish.php',
        'http://www.aquahobby.com/e_cyprinids.php',
        'http://www.aquahobby.com/e_characins.php,',
        'http://www.aquahobby.com/e_american_cichlids.php',
        'http://www.aquahobby.com/e_african_cichlids.php',
        'http://www.aquahobby.com/e_plecos_catfishes.php'

    ]

    def parse(self, response):
        for link in response.css('li').css('a::attr(href)').getall():
            if link is not None:
                yield response.follow(link, callback=self.parseMore, cb_kwargs=dict(parentalData=None))
        
    def parseMore(self, response, parentalData):
        try:
            category = response.css('span.maintitle::text').get()

            if parentalData is None:
                comments = []
                stats = {}
            else:
                comments = parentalData['Comments']
                stats = parentalData['Stats']

            for values in response.css('span.postbody').css('p'):
                if values.css('p::attr(align)').get() == 'justify':
                    comment = values.css('p::text').getall()
                    commentedit = ' '.join(com.strip() for com in comment)
                    comments.append(commentedit)
                else:
                    t1, t2 = response.css('table.profiles').css('tr')[-2:]
                    keys = t1.css('td').css('b::text').getall()[1:]
                    values = []
                    for td in t2.css('td'):
                        if td.css('td::attr(align)').get() == "center":
                            values.append(td.css('td::text').get())
                    
                    for i in range(len(keys)):
                        stats[keys[i].strip()] = values[i].strip()


            data = {
                'Category': category,
                'Comments': comments,
                'Stats' : stats
            }

            pages = response.css('span.lnav').css('a::text').getall()
            nextpage = None

            for i in range(1,len(pages)+1):
                if str(i) != pages[i-1]:
                    nextpage = response.css('span.lnav').css('a::attr(href)').getall()[i-1]
                    break
            
            if nextpage is not None:
                yield response.follow(nextpage, callback=self.parseMore, cb_kwargs=dict(parentalData=data))
            else:
                yield data
        except Exception as e:
            yield {"Error": response, "WITH": e}

class plantsAquabyNature(scrapy.Spider):
    name = "plantsAqua"

    start_urls = [
        'https://aquabynature-shop.com/59-aquatic-plants'
    ]

    def parse(self, response):
        visited = {}
        for plantlink in response.css('a.product-name'):
            title = plantlink.css('a::attr(title)').get().split('-')[0]
            link = plantlink.css('a::attr(href)').get()

            if title not in visited:
                visited[title] = True
            else:
                continue

            if link is not None:
                yield response.follow(plantlink, callback=self.parseMore)
            
        
        next_page = response.css('li#pagination_next_bottom').css('a::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parseMore(self, response):
        item = response.css('div.pb-center-column')

        name = item.css('h1::text').get().split('-')[0].strip()

        stats = {}

        for stat in item.css('div#short_description_content').css('p'):
            strongitem = stat.css('strong::text').getall()
            pitem = stat.css('p::text').getall()

            for i in range(len(pitem)):
                try:
                    stats[strongitem[i][:-1].strip()] = pitem[i].strip()
                except:
                    yield {"Error": name}

        yield {
            'Category': name,
            'Stats': stats
        }

class plantsTropica(scrapy.Spider):
    name = "plantsTropica"

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