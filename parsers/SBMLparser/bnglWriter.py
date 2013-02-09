#!/usr/bin/env python

import re
from copy import deepcopy

def bnglReaction(reactant,product,rate,tags,translator=[],isCompartments=False,reversible=True):
    finalString = ''
    #if translator != []:
    #    translator = balanceTranslator(reactant,product,translator)
    if len(reactant) == 0:
        finalString += 'Null() '
    for index in range(0,len(reactant)):
        tag = ''
        if reactant[index][0] in tags and isCompartments:
            tag = tags[reactant[index][0]]
        finalString += printTranslate(reactant[index],tag,translator)
        if index < len(reactant) -1:
            finalString += ' + '
    if reversible:
        finalString += ' <-> '
    else:
        finalString += ' -> '
    if len(product) == 0:
        finalString += 'Null() '
    for index in range(0,len(product)):
        tag = ''
        if product[index][0] in tags and isCompartments:
            tag = tags[product[index][0]]
        finalString +=  printTranslate(product[index],tag,translator) 
        if index < len(product) -1:
            finalString += ' + '
    finalString += ' ' + rate
    return finalString
    


def printTranslate(chemical,tags,translator={}):
    tmp = []
    if chemical[0] not in translator:
        app = chemical[0] + '()' + tags
    else:
        translator[chemical[0]].addCompartment(tags)
        app = str(translator[chemical[0]])
    for item in range(0,int(chemical[1])):
        tmp.append(app)
    return ' + '.join(tmp)

def balanceTranslator(reactant,product,translator):
    rMolecules = []
    pMolecules = []
    newTranslator = {}
    for species in reactant:
        if species[0] in translator:
            newTranslator[species[0]] = deepcopy(translator[species[0]]) 
            rMolecules.extend(newTranslator[species[0]].molecules)
    for species in product:
        if species[0] in translator:
            newTranslator[species[0]] = deepcopy(translator[species[0]])
            pMolecules.extend(newTranslator[species[0]].molecules)
        
    for rMolecule in rMolecules:
        for pMolecule in pMolecules:
            if rMolecule.name == pMolecule.name:
                overFlowingComponents = [x for x in rMolecule.components if x.name not in [y .name for y in pMolecule.components]]
                overFlowingComponents.extend([x for x in pMolecule.components if x.name not in [y .name for y in rMolecule.components]])                
                rMolecule.removeComponents(overFlowingComponents)
                pMolecule.removeComponents(overFlowingComponents)
    return newTranslator


    
def bnglFunction(rule,functionTitle,compartments=[]):
    def powParse(match):
        return '({0})^({1})'.format(match.group(2),match.group(3))

    tmp = rule
    #delete the compartment from the rate function since cBNGL already does it
    for compartment in compartments:
        tmp = re.sub('{0}\\s*[*]'.format(compartment),'',tmp)
        tmp = re.sub('\\*\\s*{0}'.format(compartment),'',tmp)
    #BNGL has ^ for power. 
    tmp = re.sub('(pow)\(([^,]+),([^)]+)\)',powParse,tmp)
    finalString = '%s = %s' % (functionTitle,tmp)
    return finalString

    
def finalText(param,molecules,species,observables,rules,functions,compartments,fileName):
    output = open(fileName,'w')
    output.write('begin model\n')
    output.write(sectionTemplate('parameters',param))
    output.write(sectionTemplate('compartments',compartments))          
    output.write(sectionTemplate('molecule types',molecules))
    output.write(sectionTemplate('seed species',species))
    output.write(sectionTemplate('observables',observables))
    output.write(sectionTemplate('functions',functions))
    output.write(sectionTemplate('reaction rules',rules))
    output.write('end model\n')
    output.write('generate_network();\n')
    output.write('simulate_ode({t_end=>100,n_steps=>100});')
    #output.write('writeXML()\n')
    
def sectionTemplate(name,content):
    section = 'begin %s\n' % name
    temp = ['\t%s\n' % line for line in content]
    section += ''.join(temp)
    section += 'end %s\n' % name
    return section

