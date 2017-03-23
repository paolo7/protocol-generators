# This uses the RDFLib library https://github.com/RDFLib/rdflib

import rdflib, codecs, re, string, difflib, itertools, string
from SPARQLWrapper import SPARQLWrapper, JSON
from stop_words import get_stop_words
from bs4 import BeautifulSoup

simple_i_dict = {}
index = 0


graph_name = "http://localhost:8890/Collaboration"
graph_name = "http://localhost:8890/CollaborationExtended"

def simplify_dict(uri):
    global index
    if not uri in simple_i_dict:
        simple_i_dict[uri] = "i"+str(index)
        index += 1

sparql = SPARQLWrapper("http://localhost:8890/sparql/")
prefixes = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       PREFIX prohow: <http://w3id.org/prohow#>
       PREFIX owl: <http://www.w3.org/2002/07/owl#>
       PREFIX w: <http://w3id.org/prohowlinks#>
       PREFIX oa: <http://www.w3.org/ns/oa#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX dbo: <http://dbpedia.org/ontology/>
"""
num = 0
sparql.setQuery(prefixes+"""
    SELECT DISTINCT ?pair1 ?pair2
    FROM <"""+graph_name+""">
    WHERE {
        ?pair1 owl:sameAs ?same .
        ?pair1 prohow:language prohow:language_code_en .
        ?pair2 owl:sameAs ?same .
        ?pair2 prohow:language prohow:language_code_es .
     }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    #print("P1 "+result["pair1"]["value"])
    #print("P2 "+result["pair2"]["value"])
    num += 1
print str(num)+" language pairs were found."

def same_num_rel(en_uri,es_uri,rel):
    num_en = -1
    num_es = -1
    sparql.setQuery(prefixes + """
            SELECT (COUNT(distinct ?s) AS ?no)
            FROM <"""+graph_name+""">
            WHERE {
                <""" + en_uri + """> prohow:"""+rel+""" ?s
             }
        """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        num_en = result["no"]["value"]
    sparql.setQuery(prefixes + """
                SELECT (COUNT(distinct ?s) AS ?no)
                FROM <"""+graph_name+""">
                WHERE {
                    <""" + es_uri + """> prohow:"""+rel+""" ?s
                 }
            """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        num_es = result["no"]["value"]
    return (num_es > 0 and num_en > 0) and num_es == num_en

discarded_because_unequal_steps_or_req = 0

def basic_clean(label):
    return " ".join(label.strip().split())

def basic_match(l1,l2):
    l1o = l1
    l2o = l2
    l1 = l1.lower()
    l2 = l2.lower()
    if "de" in l1:
        l1 = l1.split(' de ', 1)[-1].strip()
    if "of" in l1:
        l1 = l1.split(' of ', 1)[-1].strip()
    if l1 in l2:
        #print l1o
        #print l2o
        return True
    l1m = re.sub(r'\([^)]*\)', '', l1)
    if l1m in l2:
        #print l1o
        #print l2o
        return True
    l1m2 = re.sub('[\W_]+', '', l1m)
    l2m = re.sub('[\W_]+', '', l2)
    if l1m2 in l2m:
        #print l1o
        #print l2o
        return True
    return False

def smooth_inclusion_score(r_l,s_l):
    exclude = set(string.punctuation)
    r_l = ''.join(ch for ch in r_l if ch not in exclude)
    s_l = ''.join(ch for ch in s_l if ch not in exclude)
    r_array = [x for x in r_l.split() if (x not in get_stop_words('en') and x not in get_stop_words('es'))]
    s_array = [x for x in s_l.split() if (x not in get_stop_words('en') and x not in get_stop_words('es'))]
    #print "? "+str(r_array)
    #print "? "+str(s_array)
    if len(r_array) >= len(s_array):
        return array_inclusion(s_array,r_array)#difflib.SequenceMatcher(None, conc(r_array), conc(s_array)).ratio() - ((len(r_l)-len(s_l)) / (len(r_l)+len(s_l)))
    else:
        return array_inclusion(r_array,s_array)

def array_inclusion(small,big):
    i = 0
    best_score = -1
    while i <= len(big) - len(small):
        window = []
        w_i = i
        while w_i < i + len(small):
            window.append(big[w_i])
            w_i += 1
        i += 1
        score = 0
        wi = 0
        while wi < len(small):
            wi2 = 0
            best_token_score = 0
            while wi2 < len(small):
                token_score = difflib.SequenceMatcher(None, small[wi], window[wi2]).ratio()
                if token_score > 0.7 and token_score > best_token_score:
                    best_token_score = token_score
                wi2 +=1
            score += best_token_score
            wi += 1
        if score > best_score:
            best_score = score
    return best_score

def process_data(printout,en_uri,es_uri,en_label,es_label,req_en,req_es,type_req_en,type_req_es,step_en,step_es,step_en_a,step_es_a,dep_en,dep_es,ordered_steps_en,ordered_steps_es):
    print en_uri + " : " + en_label
    printout = False
    if printout:
        print en_uri+" : "+en_label
        for r in req_en:
            print " * Requires "+r+" : "+req_en[r]
        for r in ordered_steps_en:
            print " - Step "+r+" : "+step_en[r]
            if r in step_en_a:
                print " - Step Abstract " + r + " : " + step_en_a[r]
        print es_uri + " : " + es_label
        for d in dep_en:
            print d+" requires " + dep_en[d]
        for r in req_es:
            print " * Requires "+r+" : "+req_es[r]
        for r in req_es:
            print " * Requires "+r+" : "+req_es[r]
        for r in ordered_steps_es:
            print " - Step "+r+" : "+step_es[r]
            if r in step_es_a:
                print " - Step Abstract " + r + " : " + step_es_a[r]
        for d in dep_es:
            print d+" requires " + dep_es[d]
    req_en_step_inverse_dep = {}
    req_es_step_inverse_dep = {}
    for i, s_en in enumerate(ordered_steps_en):
        s_es = ordered_steps_es[i]
        s_en_label = basic_clean(step_en[s_en])
        s_es_label = basic_clean(step_es[s_es])
        for r in req_en:
            if r not in req_en_step_inverse_dep:
                r_label = basic_clean(req_en[r])
                if basic_match(r_label,s_en_label):
                    req_en_step_inverse_dep[r] = s_en
        for r in req_es:
            if r not in req_es_step_inverse_dep:
                r_label = basic_clean(req_es[r])
                if basic_match(r_label,s_es_label):
                    req_es_step_inverse_dep[r] = s_es
    # try with abstract
    for i, s_en in enumerate(ordered_steps_en):
        s_es = ordered_steps_es[i]
        s_en_label = basic_clean(step_en[s_en]+" "+step_en_a[s_en])
        s_es_label = basic_clean(step_es[s_es]+" "+step_es_a[s_es])
        for r in req_en:
            if r not in req_en_step_inverse_dep:
                r_label = basic_clean(req_en[r])
                if basic_match(r_label,s_en_label):
                    req_en_step_inverse_dep[r] = s_en
        for r in req_es:
            if r not in req_es_step_inverse_dep:
                r_label = basic_clean(req_es[r])
                if basic_match(r_label,s_es_label):
                    req_es_step_inverse_dep[r] = s_es
    for r in req_en:
        if r not in req_en_step_inverse_dep:
            r_l = req_en[r]
            best_score = -1
            best_step = None
            for s in ordered_steps_en:
                score = smooth_inclusion_score(r_l,step_en[s]+" "+step_en_a[s])
                if score > best_score:
                    best_score = score
                    best_step = s
            if best_score >= 1:
                req_en_step_inverse_dep[r] = best_step
                #print best_score
                #print r_l
                #print step_en[best_step]+" "+step_en_a[best_step]
    for r in req_es:
        if r not in req_es_step_inverse_dep:
            r_l = req_es[r]
            best_score = -1
            best_step = None
            for s in ordered_steps_es:
                score = smooth_inclusion_score(r_l,step_es[s]+" "+step_es_a[s])
                if score > best_score:
                    best_score = score
                    best_step = s
            if best_score >= 1:
                req_es_step_inverse_dep[r] = best_step
                #print best_score
                #print r_l
                #print step_es[best_step]+" "+step_es_a[best_step]
    dep_en_tot = {}
    dep_es_tot = {}
    for r in req_en:
        if r not in req_en_step_inverse_dep:
            req_en_step_inverse_dep[r] = ordered_steps_en[0]
    for r in req_es:
        if r not in req_es_step_inverse_dep:
            req_es_step_inverse_dep[r] = ordered_steps_es[0]
    for d in dep_en:
        if not d in dep_en_tot:
            dep_en_tot[d] = [dep_en[d]]
        else:
            dep_en_tot[d].append(d)
    for d in dep_es:
        if not d in dep_es_tot:
            dep_es_tot[d] = [dep_es[d]]
        else:
            dep_es_tot[d].append(d)
    for r in req_en_step_inverse_dep:
        d = req_en_step_inverse_dep[r]
        if not d in dep_en_tot:
            dep_en_tot[d] = [r]
        else:
            dep_en_tot[d].append(r)
    for r in req_es_step_inverse_dep:
        d = req_es_step_inverse_dep[r]
        if not d in dep_es_tot:
            dep_es_tot[d] = [r]
        else:
            dep_es_tot[d].append(r)
    # check if protocols match
    for i, s_en in enumerate(ordered_steps_en):
        s_es = ordered_steps_es[i]
        if (s_en in dep_en_tot and not s_es in dep_es_tot) or (s_es in dep_es_tot and not s_en in dep_en_tot):
            print " no match"
            return False
        if (s_en in dep_en_tot and s_es in dep_es_tot):
            if (len(dep_en_tot[s_en]) != len(dep_es_tot[s_es])):
                # try to correct the situation by sending back all the requirements of both
                for r in req_en_step_inverse_dep:
                    if req_en_step_inverse_dep[r] == s_en and i > 0:
                        # remove it from the later one
                        dep_en_tot[s_en].remove(r)
                        # add it to the first
                        if not ordered_steps_en[0] in dep_en_tot:
                            dep_en_tot[ordered_steps_en[0]] = [r]
                        else:
                            dep_en_tot[ordered_steps_en[0]].append(r)
                for r in req_es_step_inverse_dep:
                    if req_es_step_inverse_dep[r] == s_es and i > 0:
                        # remove it from the later one
                        dep_es_tot[s_es].remove(r)
                        # add it to the first
                        if not ordered_steps_es[0] in dep_es_tot:
                            dep_es_tot[ordered_steps_es[0]] = [r]
                        else:
                            dep_es_tot[ordered_steps_es[0]].append(r)
    postponed = 0
    for i, s_en in enumerate(ordered_steps_en):
        s_es = ordered_steps_es[i]
        if (s_en in dep_en_tot and s_es in dep_es_tot):
            if (len(dep_en_tot[s_en]) != len(dep_es_tot[s_es])):
                print " STRANGE no match"
                return False
            else:
                if len(dep_en_tot[s_en]) > 1 and i > 0:
                    postponed += len(dep_en_tot[s_en])-1
    if postponed < 5:
        print " no match, too few requirements assigned to steps: "+str(postponed)
        return False
    print "FOUND A MATCH "+str(postponed)
    save_pair(dep_en_tot,dep_es_tot,en_uri,es_uri,en_label,es_label,req_en,req_es,type_req_en,type_req_es,step_en,step_es,step_en_a,step_es_a,dep_en,dep_es,ordered_steps_en,ordered_steps_es)
    return True

simple_i_dictionary = {}
index_dictionary = 0

def geti(uri):
    global index_dictionary
    global simple_i_dictionary
    if not uri in simple_i_dictionary:
        simple_i_dictionary[uri] = "i"+str(index_dictionary)
        index_dictionary += 1
    return simple_i_dictionary[uri]

index_pairs = 0

def save_pair(dep_en_tot,dep_es_tot,en_uri,es_uri,en_label,es_label,req_en,req_es,type_req_en,type_req_es,step_en,step_es,step_en_a,step_es_a,dep_en,dep_es,ordered_steps_en,ordered_steps_es):
    global index_pairs
    out_label = codecs.open('all_labels.txt', 'a', "utf-8")
    #out_abstracts = open('all_abstracts.txt', 'a')
    out_dependencies = codecs.open('all_dependencies.txt', 'a', "utf-8")
    out_turtle= codecs.open('all_turtle.txt', 'a', "utf-8")
    title_both = "\n#PROTOCOLPAIR[" + str(index_pairs) + "]"+"\n"
    title_en = "#PAIR[" + str(index_pairs) + "] " + en_uri + " # " + en_label + "\n#steps:"+str(len(step_en))\
               +";req:"+str(len(req_en))+";dep:"+str(len(dep_en_tot))+";distinctReq:"\
                +str("http://w3id.org/prohow#requirement" in type_req_en.values() and "http://w3id.org/prohow#consumable" in type_req_en.values())+";\n"
    title_es = "#PAIR[" + str(index_pairs) + "] " + es_uri + " # " + es_label+"\n#steps:"+str(len(step_es))\
               +";req:"+str(len(req_es))+";dep:"+str(len(dep_es_tot))+";distinctReq:"+ \
               str("http://w3id.org/prohow#requirement" in type_req_es.values() and "http://w3id.org/prohow#consumable" in type_req_es.values())+";\n"
    index_pairs += 1

    # write the label file
    out_label.write(title_both)
    out_label.write(title_en)
    for s in step_en:
        out_label.write("st "+geti(s) + " "+(step_en[s]+" "+step_en_a[s].strip())+"\n")
    for s in req_en:
        type = "re "
        if "http://w3id.org/prohow#requirement" in type_req_en.values() and "http://w3id.org/prohow#consumable" in type_req_en.values():
            if s in type_req_en:
                if type_req_en[s] == "http://w3id.org/prohow#requirement":
                    type = "nc "
                if type_req_en[s] == "http://w3id.org/prohow#consumable":
                    type = "co "
        out_label.write(type+geti(s) + " "+req_en[s]+"\n")
    out_label.write(title_es)
    for s in step_es:
        out_label.write("st "+geti(s) + " "+(step_es[s]+" "+step_es_a[s].strip())+"\n")
    for s in req_es:
        type = "re "
        if "http://w3id.org/prohow#requirement" in type_req_es.values() and "http://w3id.org/prohow#consumable" in type_req_es.values():
            if s in type_req_es:
                if type_req_es[s] == "http://w3id.org/prohow#requirement":
                    type = "nc "
                if type_req_es[s] == "http://w3id.org/prohow#consumable":
                    type = "co "
        out_label.write(type+geti(s) + " "+req_es[s]+"\n")
    # write the dependency file
    out_dependencies.write(title_both)
    out_dependencies.write(title_en)
    for d in dep_en_tot:
        for d1 in dep_en_tot[d]:
            out_dependencies.write(geti(d1) + " " + geti(d) + "\n")
    out_dependencies.write(title_es)
    for d in dep_es_tot:
        for d1 in dep_es_tot[d]:
            out_dependencies.write(geti(d1) + " " + geti(d) + "\n")
    # write the turtle file
    out_turtle.write(title_both)
    out_turtle.write(title_en)
    for s in step_en:
        out_turtle.write(":"+geti(s) + " :label \"\"\""+(step_en[s]+" "+step_en_a[s].strip())+"\"\"\" . \n")
    for s in req_en:
        #type = "re"
        #if s in type_req_en:
        #    if type_req_en[s] == "http://w3id.org/prohow#requirement":
        #        type = "nc"
        #    if type_req_en[s] == "http://w3id.org/prohow#consumable":
        #        type = "co"
        out_turtle.write(":"+geti(s) + " :label \"\"\""+req_en[s]+"\"\"\" . \n")
        #out_turtle.write(":" + geti(s) + " :type :"+type+" \n")
    for d in dep_en_tot:
        for d1 in dep_en_tot[d]:
            out_turtle.write(":"+geti(d1) + " :next :" + geti(d) + " . \n")
    out_turtle.write(title_es)
    for s in step_es:
        out_turtle.write(":"+geti(s) + " :label \"\"\""+(step_es[s]+" "+step_es_a[s].strip())+"\"\"\" . \n")
    for s in req_es:
        #type = "re"
        #if s in type_req_es:
        #    if type_req_es[s] == "http://w3id.org/prohow#requirement":
        #        type = "nc"
        #    if type_req_es[s] == "http://w3id.org/prohow#consumable":
        #        type = "co"
        out_turtle.write(":"+geti(s) + " :label \"\"\""+req_es[s]+"\"\"\" . \n")
        #out_turtle.write(":" + geti(s) + " :type :" + type + " \n")
    for d in dep_es_tot:
        for d1 in dep_es_tot[d]:
            out_turtle.write(":"+geti(d1) + " :next :" + geti(d) + " . \n")

    # Close all writers
    out_label.close()
    #out_abstracts.close()
    out_dependencies.close()
    out_turtle.close()

def process_pair(en_uri,es_uri):
    global discarded_because_unequal_steps_or_req
    if not ( same_num_rel(en_uri,es_uri,"requires") and same_num_rel(en_uri,es_uri,"has_step") ):
        discarded_because_unequal_steps_or_req += 1
        return False
    title_en = ""
    title_es = ""
    req_en = {}
    req_es = {}
    type_req_en = {}
    type_req_es = {}
    step_en = {}
    step_es = {}
    step_en_a = {}
    step_es_a = {}
    dep_en = {}
    dep_es = {}
    sparql.setQuery(prefixes + """
                    SELECT ?label
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + en_uri + """> rdfs:label ?label
                     }
                """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        title_en = result["label"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?label
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + es_uri + """> rdfs:label ?label
                     }
                    """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        title_es = result["label"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?uri ?label ?type
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + en_uri + """> prohow:requires ?uri .
                        ?uri rdfs:label ?label
                        OPTIONAL {
                            ?uri rdf:type ?type .
                        }
                     }""")
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        req_en[result["uri"]["value"]] = result["label"]["value"]
        if "type" in result and not result["type"]["value"] is None:
            type_req_en[result["uri"]["value"]] = result["type"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?uri ?label ?type
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + es_uri + """> prohow:requires ?uri .
                        ?uri rdfs:label ?label
                    OPTIONAL {
                        ?uri rdf:type ?type .
                    }
                     }""")
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        req_es[result["uri"]["value"]] = result["label"]["value"]
        if "type" in result and not result["type"]["value"] is None:
            type_req_es[result["uri"]["value"]] = result["type"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?uri ?label ?abstract
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + en_uri + """> prohow:has_step ?uri .
                        ?uri rdfs:label ?label .
                        OPTIONAL {?uri dbo:abstract ?abstract .}
                     }""")
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        step_en[result["uri"]["value"]] = result["label"]["value"]
        if not result["abstract"]["value"] is None:
            step_en_a[result["uri"]["value"]] = result["abstract"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?uri ?label ?abstract
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + es_uri + """> prohow:has_step ?uri .
                        ?uri rdfs:label ?label .
                        OPTIONAL {?uri dbo:abstract ?abstract .}
                     } """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        step_es[result["uri"]["value"]] = result["label"]["value"]
        if not result["abstract"]["value"] is None:
            step_es_a[result["uri"]["value"]] = result["abstract"]["value"]
    #
    sparql.setQuery(prefixes + """
                    SELECT ?sa ?sb
                    FROM <"""+graph_name+""">
                    WHERE {
                        <""" + en_uri + """> prohow:has_step ?sa .
                        <""" + en_uri + """> prohow:has_step ?sb .
                        ?sa prohow:requires ?sb .
                     } """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        dep_en[result["sa"]["value"]] = result["sb"]["value"]
    #
    sparql.setQuery(prefixes + """
                        SELECT ?sa ?sb
                        FROM <"""+graph_name+""">
                        WHERE {
                            <""" + es_uri + """> prohow:has_step ?sa .
                            <""" + es_uri + """> prohow:has_step ?sb .
                            ?sa prohow:requires ?sb .
                         } """)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        dep_es[result["sa"]["value"]] = result["sb"]["value"]
    # ORDERING
    ordered_steps_en = []
    # order steps
    while len(ordered_steps_en) < len(step_en):
        found = False
        for s in step_en:
            if not s in ordered_steps_en:
                if not s in dep_en:
                    ordered_steps_en.append(s)
                    found = True
                else:
                    all_req_satisfied = True
                    #for r in dep_en[s]:
                    if not dep_en[s] in ordered_steps_en:
                        all_req_satisfied = False
                    if all_req_satisfied:
                        ordered_steps_en.append(s)
                        found = True
        if not found:
            raise Exception('ERROR: Deadlock in dependencies detected')
    ordered_steps_es = []
    # order steps
    while len(ordered_steps_es) < len(step_es):
        found = False
        for s in step_es:
            if not s in ordered_steps_es:
                if not s in dep_es:
                    ordered_steps_es.append(s)
                    found = True
                else:
                    all_req_satisfied = True
                    #for r in dep_es[s]:
                    if not dep_es[s] in ordered_steps_es:
                        all_req_satisfied = False
                    if all_req_satisfied:
                        ordered_steps_es.append(s)
                        found = True
        if not found:
            raise Exception('ERROR: Deadlock in dependencies detected')
    for s in ordered_steps_en:
        simplify_dict(s)
    for s in ordered_steps_es:
        simplify_dict(s)
    for s in req_en:
        simplify_dict(s)
    for s in req_es:
        simplify_dict(s)
    process_data(True,en_uri,es_uri,title_en,title_es,req_en,req_es,type_req_en,type_req_es,step_en,step_es,step_en_a,step_es_a,dep_en,dep_es,ordered_steps_en,ordered_steps_es)

for result in results["results"]["bindings"]:
    process_pair(result["pair1"]["value"],result["pair2"]["value"])

print "This many were discarded because of unequal number of steps and/or requirements: "+str(discarded_because_unequal_steps_or_req)
