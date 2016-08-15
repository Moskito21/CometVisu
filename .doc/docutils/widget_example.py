import json
import xml.etree.ElementTree as ET
from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.utils.code_analyzer import Lexer, LexerError, NumberLines
from os import path, makedirs

counters = {}


class WidgetExampleDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'number-lines': directives.unchanged, # integer or None
        'hide-source': directives.unchanged # true or false
    }
    has_content = True

    example_dir = path.join("cache", "widget_examples", "manual")
    screenshot_dir = path.join("doc", "manual", "examples")
    config_parts = {
        "start": '<pages xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" lib_version="8" design="%%%DESIGN%%%" xsi:noNamespaceSchemaLocation="../visu_config.xsd">',
        "meta": '<meta/>',
        "content_start": '<page name="Example">',
        "content_end": '</page>',
        "end":   '</pages>'
    }

    def run(self):
        cv_meta = None
        meta = None
        global_caption = None
        self.assert_has_content()
        source = "\n".join(self.content)
        source_path = self.state_machine.document.settings._source.split("doc/manual/", 1)[1]
        screenshot_dir = path.join("doc", "manual", path.dirname(self.state_machine.document.settings._source).split("doc/manual/", 1)[1], "_static")
        name = source_path[:-4].replace("/", "_")
        if not name in counters:
            counters[name] = 0
        else:
            counters[name] += 1
        design = "metal"

        #print("Source: '%s'" % source)
        visu_config_parts = self.config_parts.copy()
        try:
            # we need one surrouding element to prevent parse errors
            xml = ET.fromstring("<root>%s</root>" % source)
            for child in xml:
                if ET.iselement(child):
                    if child.tag == "meta":
                        # meta settings
                        meta = child
                    elif child.tag == "cv-meta":
                        # config meta settings
                        cv_meta = child
                        cv_meta.tag = "meta"
                    elif child.tag == "caption":
                        global_caption = child.text
                    else:
                        # the config example
                        config = child
        except Exception as e:
            print("Parse error: %s" % str(e))

        example_content = ET.tostring(config, encoding='utf-8')
        if cv_meta:
            example_content = b"...\n%s...\n%s" % (ET.tostring(cv_meta, encoding='utf-8'), example_content)
            visu_config_parts['meta'] = ET.tostring(cv_meta, encoding='utf-8').decode('utf-8')

        settings = {
            "selector": ".widget_container",
            "screenshots": [],
            "screenshotDir": screenshot_dir
        }
        shot_index = 0
        if meta:
            # read meta settings
            design = meta.get("design", "metal")
            settings['selector'] = meta.get("selector", ".widget_container")

            for screenshot in meta.iter('screenshot'):
                shot = {
                    "name": screenshot.get("name", name + str(shot_index)),
                    "data": {}
                }
                shot_index += 1

                for data in screenshot.iter('data'):
                    shot['data'][data.get("address", "0/0/0")] = data.text

                for caption in screenshot.iter('caption'):
                    if not 'caption' in shot:
                        shot['caption'] = caption.text
                    else:
                        shot['caption'] += caption.text

                settings['screenshots'].append(shot)

            for caption in meta.iter('caption'):
                global_caption = caption.text

        # no screenshots defined, add a default one
        if len(settings['screenshots']) == 0:
            settings['screenshots'].append({
                "name": name + str(shot_index)
            })

        # replace the design value in the config
        visu_config_parts['start'] = visu_config_parts['start'].replace("%%%DESIGN%%%", design)

        # build the real config source
        visu_config = visu_config_parts['start'] + \
            visu_config_parts['meta'] + \
            visu_config_parts['content_start'] + \
            ET.tostring(config, encoding='utf-8').decode('utf-8') + \
            visu_config_parts['content_end'] + \
            visu_config_parts['end']

        # TODO: validate against XSD

        if not path.exists(self.example_dir):
            makedirs(self.example_dir)

        with open("%s_%s.xml" % (path.join(self.example_dir, name), counters[name]), "w") as f:
            f.write("%s\n%s" % (json.dumps(settings), visu_config))

        # create the code-block
        classes = ['code', 'xml']
        # set up lexical analyzer
        try:
            tokens = Lexer(example_content, 'xml',
                           self.state.document.settings.syntax_highlight)
        except LexerError as error:
            raise self.warning(error)

        if 'number-lines' in self.options:
            # optional argument `startline`, defaults to 1
            try:
                startline = int(self.options['number-lines'] or 1)
            except ValueError:
                raise self.error(':number-lines: with non-integer start value')
            endline = startline + len(self.content)
            # add linenumber filter:
            tokens = NumberLines(tokens, startline, endline)

        res_nodes = []
        for shot in settings['screenshots']:

            reference = "_static/%s.png" % shot['name']
            options = dict(uri=reference)
            if 'caption' in shot:
                options['alt'] = shot['caption']

            image_node = nodes.image(rawsource=shot['name'], **options)
            res_nodes.append(image_node)

        if 'hide-source' not in self.options or self.options['hide-source'] != "true":
            node = nodes.literal_block(example_content, classes=classes)

            self.add_name(node)
            # if called from "include", set the source
            if 'source' in self.options:
                node.attributes['source'] = self.options['source']
            # analyze content and add nodes for every token
            for classes, value in tokens:
                # print (classes, value)
                if classes:
                    node += nodes.inline(value, value, classes=classes)
                else:
                    # insert as Text to decrease the verbosity of the output
                    node += nodes.Text(value, value)

            res_nodes.append(node)
        return res_nodes


directives.register_directive("widget_example", WidgetExampleDirective)