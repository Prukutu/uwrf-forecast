# Author: Luis E. Ortiz
# A module definining classes to create and modify namelists used in
# WRF and WPS.

from collections import OrderedDict


class Namelist:
    """ A class representing a generic WRF or WPS namelist. """

    def __init__(self, program='wrf'):

        # Check that the program kwarg is specified correctly
        assert program in ('wrf', 'wps'), 'Not a valid type!'

        # Select the correct template file based on the program kwarg
        templates = {'wrf': 'namelist.input.template',
                     'wps': 'namelist.wps.template'}

        self.TEMPLATEFILE = templates[program]
        self.program = program

        return None

    def load(self):

        """ A method to load and clean up the lines in a namelist file"""

        with open(self.TEMPLATEFILE) as f:
            templatelines = f.readlines()

            # Strip empty leading/trailing spaces and remove empty and
            # separator lines.
            cleanlines = [line.replace(' ', '').strip() for line
                          in templatelines if len(line.strip()) > 0]
        # Namelist files are divided into categories. These catergory names
        # are prepended with "&"
        # self.filelines = cleanlines
        cats = [line for line in cleanlines if line[0] == '&']

        def etafix(filelines):
            """ Hack to fix the issue with the eta_levels spanning
                multiple lines.
            """
            # Get the index location of eta_levels line.
            for line in filelines:
                if line[:10] == 'eta_levels':
                    m = filelines.index(line)
                    n = m + 11
                    # Put all levels in the same line.
                    new_eta = filelines[m].split('=') + filelines[m+1:n]
                    for k in range(2, len(new_eta)):
                        new_eta[k] = new_eta[k] + '\n'
                    new_eta_line = new_eta[0] + '=' + ''.join(new_eta[1:])

            # Delete the original eta_levels lines and insert the newly
            # constructed one.
            print m, n
            del(filelines[m:n])
            filelines.insert(m, new_eta_line)

            return filelines

        if self.program == 'wrf':
            cleanlines = etafix(cleanlines)
        self.filelines = cleanlines

        # Get the index of the start and ends of the categories
        catstart = [cleanlines.index(c) + 1 for c in cats]
        catends = [n for n, s in enumerate(cleanlines) if s == '/']

        # Store the cleaned up lines from the template file into an OrderedDict
        # with keys as the parameter names.
        fields = OrderedDict()
        for n, cat in enumerate(cats):
            catparams = OrderedDict()
            for k, l in enumerate(cleanlines[catstart[n]:catends[n]]):

                key = l.split('=')[0]
                value = l.split('=')[1].strip().split(',')
                catparams[key] = value
            fields[cat] = catparams

        self.sections = cats
        self.parameters = fields

        return fields

    def generateNamelist(self, filename):
        """ Write a namelist file based on the fields dictionary.
        """
        def buildSection(secName):
            """ Build a section of th namelist. """

            # Gather the lines within a given section name.
            # Each line is an element in a list formatted as:
            # key = val1, val2, val3 (number of values depends on parameter)
            lines = []
            lines.append(secName)
            for key in self.parameters[secName].keys():
                values = ','.join(self.parameters[secName][key])
                paramline = ' = '.join([key, values])
                lines.append(paramline)
            lines.append('/\n')

            return lines

        # Build all the lines of a namelist file and write to file.
        linestowrite = [buildSection(sec) for sec in self.sections]
        flatlines = [item for sublist in linestowrite for item in sublist]
        self.linestowrite = linestowrite
        with open(filename, 'w') as f:
            f.writelines('\n'.join(flatlines))

        return flatlines
