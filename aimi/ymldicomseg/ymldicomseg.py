import os, json, yaml, pandas as pd, subprocess

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

db = {
   'categories': pd.read_csv(os.path.join(DATA_DIR, 'categories.csv')).set_index('CodeValue'),
   'types': pd.read_csv(os.path.join(DATA_DIR, 'types.csv')).set_index('CodeValue'),
   'modifyers': pd.read_csv(os.path.join(DATA_DIR, 'modifyers.csv')).set_index('CodeValue'),
   'segmentations': pd.read_csv(os.path.join(DATA_DIR, 'segmentations.csv')).set_index('id')
}

def buildSegmentJsonBySegId(segid):
    global db
    
    seg = db['segmentations'].loc[segid]
        
    # mandatory
    json = {
        'labelID': 1,
        'SegmentDescription': seg['name'],
        'SegmentAlgorithmType': 'AUTOMATIC',
        'SegmentAlgorithmName': 'TotalSegmentator',
        'SegmentedPropertyCategoryCodeSequence': {'CodeValue': str(seg['category']), **dict(db['categories'].loc[seg['category']])},
        'SegmentedPropertyTypeCodeSequence': {'CodeValue': str(seg['type']), **dict(db['types'].loc[seg['type']])},
    }
    
    # optional
    if not pd.isnull(seg['modifyer']):
        json['SegmentedPropertyTypeModifierCodeSequence'] = {'CodeValue': str(seg['modifyer']), **dict(db['modifyers'].loc[seg['modifyer']])}
        
    if not pd.isnull(seg['color']):
        json['recommendedDisplayRGBValue'] = [int(c) for c in seg['color'].split(',')]
        
    # return
    return json


def generateJsonMeta(yaml_meta, file_list):
    global db
    
    # general properties / segment properties (keys)
    gpropk = ['ContentCreatorName', 'ClinicalTrialSeriesID', 'ClinicalTrialTimePointID', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 'BodyPartExamined']
    spropk = ['SegmentAlgorithmType', 'SegmentAlgorithmName']

    # first copy the general properties
    json_meta = {k: yaml_meta['dicomseg'][k] for k in gpropk}
    json_meta['segmentAttributes'] = []

    # build segmentAttributes
    print(yaml_meta['segments'])

    # file to seg-id mapper 
    file2segid = {seg_file: segid for segid, seg_file in yaml_meta['segments'].items()}

    # iterate all files
    for seg_file in file_list:
        assert seg_file in file2segid, f"Unknown segmentation file: {seg_file}."
        segid = file2segid[seg_file]

        # create json meta for segmentation
        json_meta['segmentAttributes'].append([{**buildSegmentJsonBySegId(segid), **{k: yaml_meta['dicomseg'][k] for k in spropk}}])
        
    # return
    return json_meta


def exportJsonMeta(yaml_file, file_list, tmp_json_file = 'temp-meta.json'):
    global db

    # safety checks
    assert os.path.isfile(yaml_file)
    assert not os.path.isfile(tmp_json_file)

    # load yml meta
    with open(yaml_file, 'r') as f:
        yml_meta = yaml.safe_load(f)

    # generate 
    json_meta = generateJsonMeta(yml_meta, file_list)

    # temporarily store json
    with open(tmp_json_file, 'w') as f:
        json.dump(json_meta, f)

    # return
    return tmp_json_file


def removeTempfile(tmp_json_file = 'temp-meta.json'):
    assert os.path.isfile(tmp_json_file)

    # remove temp file
    os.remove(tmp_json_file)