# -*- coding: utf-8 -*-
from psd_tools import PSDImage
import re
import sys
import os
import argparse
import codecs

parser = argparse.ArgumentParser(
    description="A script that converts a Photoshop file into HTML/CSS Edit")
parser.add_argument("-f", "--file", required=True)
parser.add_argument("-l", "--layer", required=False)
parser.add_argument("-s", "--skiplayers", required=False)
args, leftovers = parser.parse_known_args()

filelocation = os.getcwd()+'/'+args.file
path = os.path.dirname(os.path.realpath(__file__))

# Check file directory exists
if os.path.exists(path+'/'+re.sub('.psd', '', args.file)) is False:
    os.mkdir(path+'/'+re.sub('.psd', '', args.file))
if os.path.exists(path+'/'+re.sub('.psd', '', args.file)+'/images') is False:
    os.mkdir(path+'/'+re.sub('.psd', '', args.file)+'/images')

psd = PSDImage.open(filelocation)

elements = []


# if layer name is already used for an id append _n, where n is smallest
# availible number
def namelayer(checkname, i):
    checkname = re.sub(',', '', checkname)
    checkname = re.sub('\\.', '', checkname)
    checkname = re.sub('\\s', '-', checkname)
    checkname = re.sub('\\*', '-', checkname)
    checkname = re.sub('\\!', '-', checkname)
    checkname = re.sub('\\|', '-', checkname)
    checkname = re.sub('\\+', '-', checkname)
    checkname = re.sub('©', '', checkname)
    checkname = re.sub('@', '-', checkname)
    checkname = re.sub('&', '-', checkname)

    if(checkname in elements):
        i += 1
        # remove _n if i higher than 1
        if(i > 1):
            splitstring = checkname.split('_')
            splitstring.pop()
            checkname = ''.join(splitstring)
        return namelayer(checkname+"_"+str(i), i)
    else:
        if checkname[0].isdigit():
            return 'a'+checkname
        return checkname


def layerstoimage(psd, indent):
    global elements
    html, css = '', ''

    for layer in psd:
        # get name
        name = namelayer(layer.name, 0)
        elements.append(name)

        # errors is name is ascii chars
        # print("Processing Layer: " + name + " | Group:", layer.is_group())

        indent_txt = '        '
        for x in range(indent):
            indent_txt += '    '

        # get width
        width = layer.bbox[2] - layer.bbox[0]
        width = str(width) + 'px'

        if layer.is_group():
            if indent <= 1:
                html += indent_txt+'<div class="row ' + name + '">\n'
            else:
                html += indent_txt+'<div class="col ' + name + '">\n'
            img = layerstoimage(layer, indent+1)
            html += img[0]
            html += indent_txt+'</div>\n'
            css += img[1]
            continue

        if layer.name == args.skiplayers:
            continue

        # create html
        if layer.kind == 'type':
            '''text = layer.engine_dict['Editor']['Text'].value
            fontset = layer.resource_dict['FontSet']
            runlength = layer.engine_dict['StyleRun']['RunLengthArray']
            rundata = layer.engine_dict['StyleRun']['RunArray']
            index = 0
            for length, style in zip(runlength, rundata):
                substring = text[index:index + length]
                try:
                    print(substring)
                except:
                    pass
                index += length
            '''
            html += indent_txt+'<p class="' + name + '">' + \
                re.sub('\r', ' ', layer.text)+'</p>\n'

            fontset = layer.resource_dict['FontSet']
            stylesheet = layer.engine_dict['StyleRun']['RunArray'][0]['StyleSheet']['StyleSheetData']
            css += '.'+name+' {\n'
            css += '  font-size: ' + \
                str(int(stylesheet['FontSize']))+'px;\n'
            css += '  font-family: ' + \
                str(fontset[stylesheet['Font']]['Name']) + \
                ';\n'
            css += '  color: rgba(' + \
                str(int(stylesheet['FillColor']['Values'][3]*255)) + ', ' + \
                str(int(stylesheet['FillColor']['Values'][1]*255)) + ', ' + \
                str(int(stylesheet['FillColor']['Values'][2]*255)) + ', ' + \
                str(int(stylesheet['FillColor']['Values'][0])) + ');\n'
            css += '}\n'
        elif layer.kind == "shape" or layer.kind == "pixel":
            solid_color = False
            img_pil = layer.topil()
            img_getcolors = None
            if img_pil:
                img_getcolors = img_pil.getcolors()
                if img_getcolors and len(img_getcolors) == 2:
                    if img_getcolors[0][1][0:-1] == img_getcolors[1][1][0:-1]:
                        solid_color = True
            if not solid_color:
                img_path = path + '/' + re.sub('.psd', '', args.file) + \
                        '/images/' + name + '.png'
                html += indent_txt + '<img src="images/' + name + \
                    '.png" class="' + name + '" alt="">\n'

                if os.path.exists(img_path) is False:
                    # save images as images
                    layer_image = layer.composite()
                    layer_image.save(img_path)
            else:
                html += indent_txt + '<div class="' + name + '"></div>\n'
                css += '.'+name+' {\n'
                css += '  background-color: rgb' + \
                    str(img_getcolors[0][1][0:-1]) + ';\n'
                if layer.size[0] == psd.size[0]:
                    css += '  width: 100%;\n'
                else:
                    css += '  width: ' + str(layer.size[0]) + 'px;\n'
                css += '  height: ' + str(layer.size[1]) + 'px;\n'
                css += '}\n'
        else:
            html += indent_txt+'<div class="row-1 ' + name + '"></div>\n'
    return html, css


html = '<html>\n<head>'
html += '''
    <meta charset="utf-8">
            <!--SEO Meta Tags-->
    <title>Test Site Name</title>
    <meta name="description" content="">
              <meta name="application-name" content="Ryman Marketing Test" />
            <meta name="csrf-token" content="G2Eg3PqDRJuHvZci1EHG2nWEI5sBNj1I0tbf4vdk">
    <meta name="idempotency-token" content="wZZpYV2MeJN7vHk27ByrhAkt9Ig1iQcVkKczJXQuHEFKw83r89oAi5Kbr9Gsnfyl">
    <meta name="keywords" content="">
    <meta name="currency" content="GBP">
    <meta name="currency_iso" content="GBP">
    <meta name="country" content="IE">
    <meta name="lang" content="en_gb" />
    <meta name="blitz" content="mu-828a61bc-a033023c-c8623a71-ea8fbd04">
    <link rel="preconnect" href="https://eu.evocdn.io" crossorigin>
    <link rel="dns-prefetch" href="https://eu.evocdn.io">

    <meta name="evo_timezone" content="Europe/Dublin" />
    <meta name="evo_date_format" content="DD/MM/YYYY"/>
    <meta name="evo_time_format" content="hh:mm:ss A"/>
    <meta name="evo_datetime_format" content="DD/MM/YYYY hh:mm:ss A"/>
    <meta name="evox_trace_id" content="6dak29Brb7c265efbe208fff564ee984b55d07a5" />'''
html += '\n    <link rel="stylesheet" href="index.css">\n' + \
    '    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/cs' + \
    's/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG' + \
    '1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"' + \
    ' crossorigin="anonymous">'

html += '</head>\n\n<body>\n    ' + \
    '<div class="container-fluid">\n'
css = ''

for all_layer in psd:
    if(args.layer is None or all_layer.name == args.layer):
        if all_layer.kind != "pixel":
            html += '        <div class="container-fluid ' + \
                all_layer.name + '">\n'
            temp_site = layerstoimage(all_layer, 1)
            html += temp_site[0] + '        </div>\n'
            css += temp_site[1]
html += '</div></body>\n</html>'

f = codecs.open(path+'/'+re.sub('.psd', '', args.file) +
                '/index.html', 'w', "utf-8")
f.write(html)
f.close()

f = codecs.open(path+'/'+re.sub('.psd', '', args.file) +
                '/index.css', 'w', "utf-8")
f.write(css)
f.close()
