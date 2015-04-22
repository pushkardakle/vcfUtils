__author__ = 'pushkar'


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import logging
import vcf



# Logging setup
logging.basicConfig(format='%(asctime)s %(levelname)s : %(message)s', level=logging.INFO)


# Methods
# Tab to VCF

def tabtovcf(input_tab_seperated_text_file_path, output_file_path):

    """
    Convert a tab seprated list of CHROM, POS, REF, ALT into a vcf file according to vcf4.1 standards
    I assumes the first line to be a header If you have none keep it blank
:param input_tab_seperated_text_file_path: The path to the tab seperated input file of specified format
:param output_file_path: The path for output vcf file
:return:None
"""
    try:
        tab_sep_file = open(input_tab_seperated_text_file_path)
        vcf_out_file = open(output_file_path, "w")
    except IOError as e:
        logging.error("Could not open the file at %s" % e.filename)
        logging.debug("Error message received %s" % e.strerror)
        return None

    logging.info("Processing input file at %s" % input_tab_seperated_text_file_path)
    logging.info("Writing output to %s" % output_file_path)
    headerline = tab_sep_file.readline()  # discarding the first header line

    # Printing out the vcf headers
    vcf_out_file.write("##fileformat=VCFv4.1\n")
    vcf_out_file.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
    vcf_out_file.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tDummy_Sample\n")

    for tabline in tab_sep_file:
        tabline_list = tabline.rstrip("\n").split("\t")
        vcf_out_file.write("%s\t%s\t.\t%s\t%s\t.\t.\t.\tGT\t1/1\n" % tuple(tabline_list))


# VCF to Excel

def vcftoexcel(vcffilepath, output_file_path):

    """
    Convert given vcf file to tab seperatated excel file for easy exploration and filtering purposes
    Current implementation will break down the info feilds into individual columns
    Also for every sample only genotypes are listed
    Future implementations may has option to give a string of other format options
:param vcffilepath: The path to the input vcf file to be converted to tab seperated excel format
:param output_file_path: The path to the tab seperated output file
:return: None
"""

    # Other variable initializations
    vcf_initial_static_feilds = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER']

    # Checking if vcf file exists
    try:
        vcfhandler = vcf.Reader(open(vcffilepath))
        output_excel = open(output_file_path, 'w')
    except IOError as e:
        logging.error("Could not open the vcf file at %s" % e.filename)
        logging.debug("Error message received %s" % e.strerror)
        return None

    logging.info("Processing vcf file at %s" % vcffilepath)
    logging.info("Writing output to file %s" % output_file_path)

    # Sorting the info fields
    sorted_info_fields = sorted(vcfhandler.infos.keys())

    # Writing the output header
    start_static_feilds = '\t'.join(vcf_initial_static_feilds)

    if sorted_info_fields[0]:
        info_line = '\t'.join(sorted_info_fields)  # Combine all the info feilds into a tab seperated string
    else:
        info_line = '\tINFO'

    samples_line = '_GT\t'.join(vcfhandler.samples) + "_GT"  # Combine all sample names with GT tag
    output_excel.write("%s\t%s\t%s\n" % (start_static_feilds, info_line, samples_line))  # Write header

    # Iterate over each record
    for vcfSingleRecord in vcfhandler:
        # Printing the static feilds
        vcf_record_excel_construct = ""  # Initializing a blank record
        for static_feild in vcf_initial_static_feilds:  # Iterating over staring static fields
            if vcf_record_excel_construct:
                vcf_record_excel_construct += "\t" + __format_fields(vcfSingleRecord.__getattribute__(static_feild))
            else:
                vcf_record_excel_construct = __format_fields(vcfSingleRecord.__getattribute__(static_feild))

        # Iterating over the info feilds
        for info_field in sorted_info_fields:
            if info_field in vcfSingleRecord.INFO.keys():
                vcf_record_excel_construct += "\t" + __format_fields(vcfSingleRecord.INFO[info_field])
            else:
                vcf_record_excel_construct += "\t---"

        # Iterating over samples for genotypes
        for sample_name in vcfhandler.samples:
            vcf_record_excel_construct += "\t" + __format_genotypes(vcfSingleRecord.genotype(sample_name).gt_nums)

        # Printing out the records
        output_excel.write("%s\n" % vcf_record_excel_construct)

    output_excel.close()


def __format_genotypes(field):
    return_formatted_field = "___UNKNOWNFEILDFORMATTING___"
    if field:
        if type(field) == str:
            return_formatted_field = field
        else:
            return_formatted_field = "___UNKNOWNFEILDFORMATTING___"
    else:
        return_formatted_field = "./."
    return return_formatted_field.strip('\'')


def __format_fields(field):
    return_formatted_field = "___UNKNOWNFEILDFORMATTING___"
    if field:
        if type(field) == int or type(field) == float:
            return_formatted_field = str(field)
        elif type(field) == list:
            if field[0]:
                return_formatted_field = str(field).strip('[]').replace('\', \'', ',')
            else:
                return_formatted_field = "---"
        elif type(field) == bool and field:
            return_formatted_field = "Yes"
        elif type(field) == str:
            return_formatted_field = str(field)
        else:
            return_formatted_field = "___UNKNOWNFEILDFORMATTING___"
    else:
        if (type(field) == int or type(field) == float) and field == 0:
            return_formatted_field = str(field)
        else:
            return_formatted_field = "---"
    return return_formatted_field.strip('\'')