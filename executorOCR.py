# Import modules
import spacy
from spacy.matcher import Matcher
import argparse
import json
from pdf2image import convert_from_path
import pytesseract
import timeit

# Initializing environment variables and process
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
nlp= spacy.load("es_core_news_md")
matcher= Matcher(nlp.vocab)

# Defining Functions
def generateTxt(name_file):
    print('[INFO]: Processing PDF file ...')
    flag_generator= True
    out_file_txt= ''
    name_file= 'PDFs\\'+name_file
    try :
        images= convert_from_path(name_file, poppler_path = r'C:\\Program Files\\poppler-0.68.0\\bin')
        # Output process
        print('[INFO]: ---Writing new Text File to disk ...')
        out_file_txt= "out_tmp_file.txt"
        f = open(out_file_txt, 'w+')
        for i in range(len(images)):
            file_out= pytesseract.image_to_string(images[i], lang='spa')
            pagina = '-------------------- Page '+ str(i)+ ' ---------------------\n'
            f.write(pagina)
            f.write(file_out)
        f.close()
        print('[INFO]: ---Ending process PDF file ...')

    except :
        flag_generator= False
    return flag_generator, out_file_txt
#
def loadPatterns(patterns_file):
    print('[INFO]: Loading Patterns Parameters ...')
    lines= patterns_file.readlines()
    i= 0
    for line in lines:
        arr_patterns= []
        i += 1
        line= line.rstrip('\n')
        words= line.split(' ')
        for word in words:   
            arr_patterns.append({'ORTH': word})
        # Pattern rule
        nom_pattern= 'rule_'+str(i)
        matcher.add(nom_pattern, [arr_patterns])
        # print(arr_patterns)
#
def findPatterns(fileList):
    print('[INFO]: Searching Patterns in TXT File Generated ...')
    num_linea= 0
    arr_dict= []
    for linea in fileList:
        linea= linea.rstrip('\n')   
        doc= nlp.make_doc(linea)
        matches= matcher(doc)
        if (len(matches)>0):
            for match_id, start, end in matches:
                match_span= doc[start: end]
                id_match= nlp.vocab.strings[match_id]
                itemFound= {'Id': id_match, 'Key': match_span.text, 'Line': num_linea, 'Word': start}
                arr_dict.append(itemFound)
        num_linea += 1
    return dict({'results': arr_dict})              
#
def loadTxt(input_file):
    print('[INFO]: Loading TXT File Generated ...')
    arr_file= input_file.readlines()
    return arr_file
#
def analyzerType1(dlist):
    resultList= []
    # Sub-patterns formulation
    matcher_sub= Matcher(nlp.vocab)
    pattern_sub= [{"ORTH": "CONCEPTO"}, {"IS_PUNCT": True}]
    matcher_sub.add("p1", [pattern_sub])
    pattern_sub= [{"ORTH": "AÑO"}, {"IS_PUNCT": True}]
    matcher_sub.add("p2", [pattern_sub])
    pattern_sub= [{"ORTH": "PERIODO"}]
    matcher_sub.add("p3", [pattern_sub])
    pattern_sub= [{"ORTH": "No"}, {"ORTH": "."}, {"ORTH": "DE"}, {"ORTH": "EXPEDIENTE"}, {"IS_PUNCT": True}]
    matcher_sub.add("p4", [pattern_sub])
    pattern_sub = [{"ORTH": "NIT"}, {"ORTH": "D.V"}, {"ORTH": "Razón"}, {"ORTH": "Social"}, {"ORTH": "Clase"}, {"ORTH": "Contribuyente"}]
    matcher_sub.add("p5", [pattern_sub])
    pattern_sub = [{"ORTH": "Dirección"}, {"ORTH": "Departamento"}, {"ORTH": "Municipio"}]
    matcher_sub.add("p6", [pattern_sub])
    #
    for num_line in range(len(dlist)):
        text= dlist[num_line].rstrip('\n')
        doc= nlp(text)
        matches= matcher_sub(doc)
        for match_id, start, end in matches:
            span= doc[start: end]
            id_match= nlp.vocab.strings[match_id]

            if id_match=='p4':
                resultList.append({doc[start: end].text.rstrip(':') : doc[end: end+4].text})
            elif id_match=='p5':
                next_line= dlist[num_line+1].rstrip('\n')
                next_line= next_line.split(' ')
                tot_next_line= len(next_line)
                resultList.append({'NIT': next_line[0]+'-'+next_line[1]})
                valor= ''
                for i in range(2, tot_next_line-2, 1):
                    valor= valor + next_line[i] + ' '
                resultList.append({'CONTRIBUYENTE': valor.rstrip(' ')})
            elif id_match=='p6':
                next_line= dlist[num_line+1].rstrip('\n')
                next_line= next_line.split(' ')
                tot_next_line= len(next_line)
                valor= ''
                for i in range(0, tot_next_line-4, 1):
                    valor= valor + next_line[i] + ' '
                # Include City and Department
                valor= valor + next_line[-1]+" ("+next_line[-3]+")"
                resultList.append({'DIRECCION': valor.rstrip(' ')})
            else :
                resultList.append({doc[start: end].text.rstrip(':') : doc[end: end+1].text.lstrip(':')})
    #
    print('[INFO]: ---Printing results ...')
    out_dict= {'results': resultList}
    print(out_dict)
    return out_dict
#
def analyzerType3(dlist):
    resultList= []
    # Sub-patterns formulation
    matcher_sub= Matcher(nlp.vocab)
    pattern_sub= [{"ORTH": "CONCEPTO"}, {"IS_PUNCT": True}]
    matcher_sub.add("p1", [pattern_sub])
    pattern_sub= [{"ORTH": "AÑO"}, {"IS_PUNCT": True}]
    matcher_sub.add("p2", [pattern_sub])
    pattern_sub= [{"ORTH": "PERIODO"}]
    matcher_sub.add("p3", [pattern_sub])
    pattern_sub= [{"ORTH": "No"}, {"ORTH": "."}, {"ORTH": "DE"}, {"ORTH": "EXPEDIENTE"}, {"IS_PUNCT": True}]
    matcher_sub.add("p4", [pattern_sub])
    pattern_sub = [{"ORTH": "Razón"}, {"ORTH": "Social"}]
    matcher_sub.add("p5", [pattern_sub])
    pattern_sub = [{"ORTH": "Dirección"}, {"ORTH": "Departamento"}, {"ORTH": "Municipio"}]
    matcher_sub.add("p6", [pattern_sub])
    for num_line in range(len(dlist)):
        text= dlist[num_line].rstrip('\n')
        doc= nlp(text)
        matches= matcher_sub(doc)
        # features= []
        # for token in doc:
        #     features.append({'token' : token.text, 'pos' : token.pos_})
        # print(features)
        for match_id, start, end in matches:
            span= doc[start: end]
            id_match= nlp.vocab.strings[match_id]
            # print(id_match, span.text, start, end)
            if id_match=='p1':
                resultList.append({'CONCEPTO' : doc[end: end+1].text.lstrip(':')})
            elif id_match=='p2':
                resultList.append({'AÑO' : doc[end: end+1].text.lstrip(':')})
            elif id_match=='p3':
                resultList.append({'PERIODO' : doc[end: end+1].text.lstrip(':')})
            elif id_match=='p4':
                resultList.append({doc[start: end].text.rstrip(':') : doc[end: end+4].text})
            elif id_match=='p5':
                next_line= dlist[num_line+1].rstrip('\n')
                next_line= next_line.split(' ')
                tot_next_line= len(next_line)
                resultList.append({'NIT': next_line[0]+'-'+next_line[1]})
                valor= ''
                for i in range(2, tot_next_line-2, 1):
                    valor= valor + next_line[i] + ' '
                resultList.append({'CONTRIBUYENTE': valor.rstrip(' ')})
            elif id_match=='p6':
                next_line= dlist[num_line+1].rstrip('\n')
                next_line= next_line.split(' ')
                tot_next_line= len(next_line)
                valor= ''
                for i in range(0, tot_next_line-4, 1):
                    valor= valor + next_line[i] + ' '
                # Include City and Department
                valor= valor + next_line[-1]+" ("+next_line[-3]+")"
                resultList.append({'DIRECCION': valor.rstrip(' ')})
    #
    print('[INFO]: ---Printing results ...')
    out_dict= {'results': resultList}
    print(out_dict)
    return out_dict

#
# Function to check the initial parameters
def input_parse():
    description = ('Inspector de Patrones...')
    p = argparse.ArgumentParser(description= description)
    p.add_argument('-tipo', '--tipo', default=None, type=str,
                   help='-tipo 1', required=True)
    p.add_argument('-input_file', '--input_file', default=None, type=str,
                   help='path/to/texto.txt', required=True)
    args = p.parse_args()
    return args
# Main Function
def main(tipo, input_file):
    json_file= open('results.json', 'w', encoding='UTF8')
    start_exec= timeit.default_timer()
    flag, out_file_txt=  generateTxt(input_file)
    end_exec= timeit.default_timer()
    print(f'[INFO]: ---Exec Time= {end_exec-start_exec} seg.')
    if flag:
        file_input= open(out_file_txt, 'r', encoding='latin-1')
        try: 
            patterns_file= 'patterns_type'+tipo+'.txt'
            file_patterns= open(patterns_file, 'r', encoding='UTF8')
        
            loadPatterns(file_patterns)
            fileList= loadTxt(file_input)

            results= findPatterns(fileList)
            # print(results)
            resultsOut= results['results']
            size_resultsOut= len(resultsOut)
            if tipo=='1' and size_resultsOut>1:
                print('[INFO]: Execution Type 1: Proceso determinación de impuestos ...')
                flag= False
                while (not flag):
                    for i in range(size_resultsOut-1):
                        if ((resultsOut[i+1]['Line']-resultsOut[i]['Line'])<60) and (resultsOut[i]['Id']=='rule_1' and resultsOut[i+1]['Id']=='rule_2'):
                            flag= True
                            json_object= analyzerType1(fileList[resultsOut[0]['Line']+1 : resultsOut[1]['Line']+2])
                            json.dump(json_object, json_file, ensure_ascii=False)
                            break
                    break
                if not flag:
                    message= 'Execution Type 1: Records not found ...'
                    print(message)
                    json.dump({'message' : message}, json_file)
            else :   
                if tipo=='3' and size_resultsOut>1:
                    print('[INFO]: Execution Type 3: Proceso Emplazamiento para Declarar ...')
                    flag= False
                    while (not flag):
                        for i in range(size_resultsOut-1):
                            if ((resultsOut[i+1]['Line']-resultsOut[i]['Line'])<60) and (resultsOut[i]['Id']=='rule_1' and resultsOut[i+1]['Id']=='rule_2'):
                                flag= True
                                json_object= analyzerType3(fileList[resultsOut[0]['Line']+1 : resultsOut[1]['Line']+2])
                                json.dump(json_object, json_file, ensure_ascii=False)
                                break
                        break
                    if not flag:
                        message= 'Execution Type 3: Records not found ...'
                        print(message)
                        json.dump({'message' : message}, json_file)
                else :
                    message= '***Execution Type not allowed ... '
                    print(message)
                    json.dump({'message' : message}, json_file)

            # Closing files  
            file_input.close()
            file_patterns.close()

        except FileNotFoundError:
            message= '***File Patterns Parameters Not Found ...'
            print(message)
            json.dump({'message' : message}, json_file)
    else :
        message= '***PDF File Error: '+input_file+' file not found in directory ...'
        print(message)
        json.dump({'message' : message}, json_file)
    #
    json_file.close()
#
if __name__=='__main__':
    args = input_parse()
    main(**vars(args))