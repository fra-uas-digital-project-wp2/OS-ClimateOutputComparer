# ============================================================================================================================
# PDF_Analyzer
# File   : HTMLDirectory.py
# Author : Ismail Demir (G124272)
# Date   : 12.06.2020
#
# Note   : 1 HTMLDirectory consistens of * HTMLPages
# Note   : 1 HTMLDirectory corresponds to 1 PDF-File
# ============================================================================================================================
from HTMLPage import HTMLPage
from Format_Analyzer import *
import shutil


class HTMLDirectory:
    htmlpages = None
    src_pdf_filename = None

    def __init__(self):
        self.htmlpages = []
        self.src_pdf_filename = None

    @staticmethod
    def call_pdftohtml(infile, outdir):
        """
        System Call "pdftohtml.exe". Converts PDF to HTML

        Args:
            infile (str): Path to the PDF file.
            outfile (str): Directory to store HTML files.

        Returns:
            None
        """
        print_verbose(2, '-> call pdftohtml_mod ' + infile)
        os.system(
            config_for_rb.global_exec_folder + r'/pdftohtml_mod/pdftohtml_mod "' + infile + '" "' + remove_trailing_slash(
                outdir) + '"')  # TODO: Specify correct path here!

    @staticmethod
    def fix_strange_encryption(html_dir):
        html_dir = remove_trailing_slash(html_dir)

        pathname = html_dir + '/page*.html'
        print_verbose(2, "Fixing strange encryption = " + str(pathname))

        for f in glob.glob(pathname):
            print_verbose(3, "---> " + str(f))
        # HTMLPage.fix_strange_encryption(f) ### TODO:  This might be needed, because there are some PDFs with some strange encryption in place (but so far not in the ESG context).

    @staticmethod
    def convert_pdf_to_html(pdf_file, info_file_contents, out_dir=None):
        """
        Cleans target dir for PDF to HTML conversion.
        Calls PDF to HTML function.

        Args:
            pdf_file (str): Path to the PDF file.
            info_file_contents (dict): Information loaded from an info file.
            out_dir (str): Directory to store HTML files.

        Returns:
            None
        """
        out_dir = get_html_out_dir(pdf_file) if out_dir is None else remove_trailing_slash(out_dir)

        try:
            shutil.rmtree(out_dir)
        except OSError:
            pass
        HTMLDirectory.call_pdftohtml(pdf_file, out_dir)

        # fix strange encryption
        HTMLDirectory.fix_strange_encryption(out_dir)

        f = open(out_dir + '/info.txt', 'w')
        f.write(info_file_contents[pdf_file])
        f.close()

    def read_pdf_filename(self, html_dir):
        with open(remove_trailing_slash(html_dir) + '/info.txt') as f:
            self.src_pdf_filename = f.read()
            print_verbose(2, 'PDF-Filename: ' + self.src_pdf_filename)

    def parse_html_directory(self, html_dir, page_wildcard):

        """
        Parses the contents of a HTML Directory into a data structure.

        Args:
            html_dir (str): HTML Directory of current pdf.
            page_wildcard (str): String used to filter pages in HTML Directory.

        Returns:
            None
        """

        html_dir = remove_trailing_slash(html_dir)

        pathname = html_dir + '/' + page_wildcard
        print_verbose(1, "PARSING DIR = " + str(pathname))

        self.read_pdf_filename(html_dir)

        for f in glob.glob(pathname):
            print_verbose(1, "ANALYZING HTML-FILE = " + str(f))

            htmlpage = HTMLPage.parse_html_file(html_dir, f)

            print_verbose(1, "Discovered tables: ")

            print_verbose(1, htmlpage.repr_tables_only())

            print_verbose(1, "Done with page = " + str(htmlpage.page_num))

            self.htmlpages.append(htmlpage)

    def render_to_png(self, base_dir, out_dir):
        """Converts HTMLPages into PNGs.

        Args:
            base_dir (str): Path to HTMLDirectory
            out_dir (str): Path to save pngs of HTMLPages.
        """
        for it in self.htmlpages:
            print_verbose(1, "Render to png : page = " + str(it.page_num))
            it.render_to_png(remove_trailing_slash(base_dir), remove_trailing_slash(out_dir))

    def print_all_tables(self):
        for it in self.htmlpages:
            print(it.repr_tables_only())

    def save_to_dir(self, out_dir):
        """Serializes parsed HTMLDirectory and saves further objects in special files.

        Args:
            out_dir (str): Directory path to save data.
        """
        for it in self.htmlpages:
            print_verbose(1, "Save to JSON and CSV: page = " + str(it.page_num))
            it.save_to_file(remove_trailing_slash(out_dir) + r'/jpage' + "{:05d}".format(it.page_num) + '.json')
            it.save_all_tables_to_csv(out_dir)
            it.save_all_footnotes_to_txt(out_dir)

    def load_from_dir(self, html_dir, page_wildcard):
        """Loads HTMLDirectory (Report) from JSON files.

        Args:
            html_dir (str): Directory Path to HTMLDirectory.
            page_wildcard (str): Wildcard determining for which JSON files to filter.
        """

        html_dir = remove_trailing_slash(html_dir)
        pathname = html_dir + '/' + page_wildcard

        self.read_pdf_filename(html_dir)

        for f in glob.glob(pathname):
            print_verbose(1, "LOADING JSON-FILE = " + str(f))
            htmlpage = HTMLPage.load_from_file(f)
            self.htmlpages.append(htmlpage)
