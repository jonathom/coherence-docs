from terracatalogueclient import Catalogue
import datetime as dt

catalogue = Catalogue()

mol = {"west": 4.38, "south": 51.21, "east": 4.42, "north": 51.24}

# give one date, find closest acqusition before and after
event = dt.date(2021, 10, 15) # input

before = event - dt.timedelta(days = 6)
after = event + dt.timedelta(days = 14)

print(["[CATALOGUE]: starting search for scenes...")

# first search
cat_before = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = before,
	end = event,
	bbox = mol
)

prod_before = {"date": None, "id": None, "path": None, 
			"orbitDirection": None, "relativeOrbitNumber": None}

# find the product closest to event date, save direction and rel orbit
for p in cat_before:
	if prod_before["date"] is None:
		prod_before["date"] = p.beginningDateTime
		prod_before["id"]  = p.id
		prod_before["path"] = "/data/MTDA/CGS_S1/" + p.data[0].href[53:]
		prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
		prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
	else:
		if p.beginningDateTime > prod_before["date"]:
			prod_before["date"] = p.beginningDateTime
			prod_before["id"] = p.id
			prod_before["path"] = "/data/MTDA/CGS_S1/" + p.data[0].href[53:]
			prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
			prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
		else:
			pass

print("[CATALOGUE]: found first scene at: ", prod_before["path"])

# quary for second product given the direction and rel orbit
cat_after = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = event + dt.timedelta(days = 1),
	end = after,
	bbox = mol,
	orbitDirection = prod_before["orbitDirection"],
	relativeOrbitNumber = prod_before["relativeOrbitNumber"]
)

prod_after = {"date": None, "id": None, "path": None}

# find the closest one to event date
for p in cat_after:		
	if prod_after["date"] is None:
		prod_after["date"] = p.beginningDateTime
		prod_after["id"]  = p.id
		prod_after["path"] = "/data/MTDA/CGS_S1/" + p.data[0].href[53:]
	else:
		if p.beginningDateTime < prod_after["date"]:
			prod_after["date"] = p.beginningDateTime
			prod_after["id"] = p.id
			prod_after["path"] = "/data/MTDA/CGS_S1/" + p.data[0].href[53:]
		else:
			pass
			
print("[CATALOGUE]: found matching scene at: ", prod_after["path"])

# TODO: Copy workflow here
import stsa
ana_split = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
ana_split.load_data(zip_path = prod_before["path"])
# TODO: figure our how to compare boundingbox to ana_split data to extract subswaths and bursts...

