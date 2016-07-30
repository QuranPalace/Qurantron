def parseQuranMetadata(resourceFile):
    import json
    with open(resourceFile) as f:
        metadata = json.loads(f.read())
    return metadata

def parseQuranTokens(corpusFile):
    tokens = {}
    with open(corpusFile) as file:
        for line in file:
            address, form, pos, feature = line.split("\t")
            features = dict([(a+":").split(":")[:2] for a in feature.strip().split("|")])
            features["form"] = form
            features["pos"] = pos
            sure,aye,kalame,token = [int(x) for x in address.strip()[1:-1].split(":")]
            if sure not in tokens: tokens[sure] = {}
            if aye not in tokens[sure]: tokens[sure][aye] = {}
            if kalame not in tokens[sure][aye]: tokens[sure][aye][kalame] = {}
            if token not in tokens[sure][aye][kalame]: tokens[sure][aye][kalame][token] = features
    return tokens

def saveTo(d,filename):
    import json
    with open(filename,"w") as f:
        f.write(json.dumps(d))

def loadFrom(filename):
    import json
    with open(filename) as f:
        d = json.loads(f.read())
    return d

def saveGraphToGDF(graph,gfdfile):
    with open(gfdfile,"w") as f:
        f.write("nodedef> name VARCHAR,label VARCHAR\n")
        for root in graph.keys():
            f.write("%s,\"%s\"\n"%(root,root))
        f.write("edgedef> node1,node2,weight DOUBLE,directed BOOLEAN\n")
        for a in graph.keys():
            for b in graph[a].keys():
                f.write("%s,%s,%f,true\n"%(a,b,graph[a][b]))


def dbInsertQuranMetadata(db,metadata):
    qurandb = db.quran

    #// [start, ayas, order, rukus, name, tname, ename, type]
    #[0, 7, 5, 1, "الفاتحة", "Al-Faatiha", "The Opening", "Meccan"],
    suras = []
    i = 0
    qurantextfile = open("text/quran-simple.txt","r")
    quransimplefile = open("text/quran-simple-clean.txt","r")

    transfiles = []
    import os
    for fname in os.listdir("trans"):
        transfiles.append((fname.split(".")[0],fname.split(".")[1],open("trans/"+fname,"r")))

    for sure in metadata["Sura"]:
        if len(sure)>2:
            transdocs = []
            i += 1
            suradoc = {"startaye":sure[0],
                        "length":sure[1],
                        "order": i,
                        "norder":sure[2],
                        "ruku":[],
                        "page":[],
                        "recommended_sajda":[],
                        "obligatory_sajda":[],
                        "name":sure[4],
                        "tname":sure[5],
                        "ename":sure[6],
                        "where":sure[7],
                        "ayat":[],
                        }
            for j in range(sure[1]):
                ayedoc = {}
                qaid = i*1000 + j
                ayedoc["order"] = j
                ayedoc["quranid"] = qaid
                ayedoc["text"] = qurantextfile.readline().strip()
                ayedoc["simple"] = quransimplefile.readline().strip()
                for translation in transfiles:
                    transdocs.append({"author":translation[1],"aye_id":qaid,"lang":translation[0],"text":translation[2].readline().strip()})
                suradoc["ayat"].append(ayedoc)
            for ruku in metadata["Ruku"]:
                if len(ruku)>1 and ruku[0]==i:
                    suradoc["ruku"].append(ruku[1])
            for page in metadata["Page"]:
                if len(page)>1 and page[0]==i:
                    suradoc["page"].append(page[1])
            for sajda in metadata["Sajda"]:
                if len(sajda)>2 and sajda[0]==i:
                    suradoc[sajda[2]+"_sajda"].append(sajda[1])
            print(suradoc["order"])
            qurandb.sura.insert_one(suradoc)
            qurandb.translation.insert_many(transdocs)

def dbInsertQuranTokens(db,tokens):
    qurandb = db.quran


if __name__ == '__main__':
    import os.path

    rootWeights = {}

    corpusfile = "corpus.json"
    if os.path.exists(corpusfile):
        tokens = loadFrom(corpusfile)
    else:
        tokens = parseQuranTokens("quranic-corpus-morphology-0.4.txt")
        saveTo(tokens,corpusfile)
    print("tokens:", len(tokens))

    metadata = parseQuranMetadata("quran-data.js")

    from pymongo import MongoClient
    db = MongoClient("mongodb://quranpalace.com:27017/admin")
    #dbInsertQuranMetadata(db,metadata)
    dbInsertQuranTokens(db,tokens)
