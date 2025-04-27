import json
import os
import uuid

with open('templates.json') as templateFile:
    templateStr = templateFile.read()

def getTemplate(name):
    templates = json.loads(templateStr)
    template = templates[name]
    template['GUID'] = str(uuid.uuid4())[:6]
    return template

def createCardEntry(data):
    card = getTemplate('cardEntry')
    card['FaceURL'] = data['front_png_url']
    card['BackURL'] = data['back_png_url']
    return dict(card)

def createCard(cardID, cardEntry):
    card= getTemplate('card')
    card['CardID'] = int(cardID)*101
    card['CustomDeck'] = {cardID:cardEntry}
    return card
    
def createDeck(data, name):
    deck = getTemplate('deck')
    deck['CustomDeck'] = {str(i+1):createCardEntry(data[cardEntry]) for i,cardEntry in enumerate(data)}
    deck['DeckIDs'] = [int(k) * 101 for k in deck['CustomDeck'].keys()]
    deck['Nickname'] = name
    deck['ContainedObjects'] = [createCard(cardId, entry) for cardId, entry in deck['CustomDeck'].items()]
    return deck
    
def createTile(name, data, faction, tags):
    tile = getTemplate('tile')
    tile['Tags'] = tags
    tile['CustomImage']['ImageURL'] = data['front_png_url']
    if data['back_png_url'] == "":
        tile['CustomImage']['ImageSecondaryURL'] = tile['CustomImage']['ImageURL']
    else:
        tile['CustomImage']['ImageSecondaryURL'] = data['back_png_url']
    tile['Nickname'] = name
    return tile
    
def createCounterBox(data, faction, name):
    bag = getTemplate('bag')
    bag['Nickname'] = name
    tags = [faction]
    bag['Tags'] = tags
    for country, formations in data.items():
        countrytags =[*tags, country]
        countryBag = getTemplate('bag')
        countryBag['Nickname'] = country;
        countryBag['Tags'] = countrytags
        for formation, units in formations.items():
            formationTags = [*countrytags, formation]
            formationBag = getTemplate('bag')
            formationBag['Nickname'] = formation
            formationBag['Tags'] = formationTags
            formationBag['ContainedObjects'] = [createTile(unit, units[unit], faction, formationTags) for unit in units ]
            countryBag['ContainedObjects'].append(formationBag)
        bag['ContainedObjects'].append(countryBag)
    return bag

with open('Red_Strike_V1_2.vmod_factions.json') as factionsFile, open('Red_Strike_V1_2.vmod_cards.json') as cardsFile:
    factionsData =json.loads(factionsFile.read())
    cardsData =json.loads(cardsFile.read())
    
counterBag = getTemplate('bag')
counterBag['Nickname'] = 'Generated Counters'
counterBag['ContainedObjects'] = [
    createCounterBox(factionsData['NATO Units'],'NATO','NATO'), 
    createCounterBox(factionsData['WP Units'],'Pact','WP'),
    createDeck(cardsData['NATO Cards'],'NATO Cards'),
    createDeck(cardsData['WP Cards'],'Pact Cards')]

ttsSave = getTemplate('ttsSave')
ttsSave['ObjectStates'] = [counterBag]
with open('RS89_Tokens.json','w') as counterFile:
    json.dump(ttsSave,counterFile, indent=4)
    