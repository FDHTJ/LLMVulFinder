import difflib
import json


def find_deleted_and_modified_lines(old_lines, new_lines):
    with open("old.cpp",'w', encoding='utf-8') as f:
        f.write(old_lines)
    with open("new.cpp",'w', encoding='utf-8') as f:
        f.write(new_lines)
    with open("old.cpp", 'r', encoding='utf-8') as f:
        old_lines = f.readlines()
    with open("new.cpp", 'r', encoding='utf-8') as f:
        new_lines = f.readlines()

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

    deleted = []
    modified = []
    flag=False
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'delete':
            for idx, line in enumerate(old_lines[i1:i2]):
                if line.strip().replace("\n","").replace("\t",'').replace(" ","") == '':continue
                flag=True
                deleted.append({
                    'line_number': i1 + idx + 1,
                    'content': line.rstrip('\n')
                })
        elif tag == 'replace':
            for idx, line in enumerate(old_lines[i1:i2]):
                if line.strip().replace("\n","").replace("\t",'').replace(" ","") == '':continue
                flag=True
                modified.append({
                    'line_number': i1 + idx + 1,
                    'original_content': line.rstrip('\n')
                })

    return {
        'deleted': deleted,
        'modified': modified
    } #if flag else None
def get_vunerable_lines(data_file):
    with open(data_file,'r', encoding='utf-8') as f:
        datas=json.load(f)
        processed_data=[]
        count=0
        for d in datas:
            d["diffs"] = find_deleted_and_modified_lines(d["func_before"], d["func_after"])
            processed_data.append(d)
        output_file=data_file.split(".json")[0]+"_with_vunerable_lines.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data,f,ensure_ascii=False,indent=4)