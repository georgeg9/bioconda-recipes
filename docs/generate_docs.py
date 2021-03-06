import os
import os.path as op
from conda_build.metadata import MetaData
from distutils.version import LooseVersion
#import matplotlib
#matplotlib.use("agg")
#import matplotlib.pyplot as plt
#from wordcloud import WordCloud


BASE_DIR = op.dirname(op.abspath(__file__))
RECIPE_DIR = op.join(op.dirname(BASE_DIR), 'recipes')
OUTPUT_DIR = op.join(BASE_DIR, 'recipes')

README_TEMPLATE = u"""\
.. _`{title}`:

{title}
{title_underline}

{summary}

======== ===========
Home     {home}
Versions {versions}
License  {license}
Recipe   {recipe}
======== ===========

Installation
------------

.. highlight: bash

With an activated Bioconda channel (see :ref:`setup`), install with::

   conda install {title}

and update with::

   conda update {title}

{notes}
"""


def setup(*args):
    """
    Go through every folder in the `bioconda-recipes/recipes` dir
    and generate a README.rst file.
    """
    print('Generating package READMEs...')
    summaries = []
    for folder in os.listdir(RECIPE_DIR):
        # Subfolders correspond to different versions
        versions = []
        for sf in os.listdir(op.join(RECIPE_DIR, folder)):
            if not op.isdir(op.join(RECIPE_DIR, folder, sf)):
                # Not a folder
                continue
            try:
                LooseVersion(sf)
            except ValueError:
                print("'{}' does not look like a proper version!".format(sf))
                continue
            versions.append(sf)
        versions.sort(key=LooseVersion, reverse=True)
        # Read the meta.yaml file
        try:
            metadata = MetaData(op.join(RECIPE_DIR, folder))
            if metadata.version() not in versions:
                versions.insert(0, metadata.version())
        except SystemExit:
            if versions:
                metadata = MetaData(op.join(RECIPE_DIR, folder, versions[0]))
            else:
                # ignore non-recipe folders
                continue

        # Format the README
        notes = metadata.get_section('extra').get('notes', '')
        if notes:
            notes = 'Notes\n-----\n\n' + notes
        summary = metadata.get_section('about').get('summary', '')
        summaries.append(summary)
        template_options = {
            'title': metadata.name(),
            'title_underline': '=' * len(metadata.name()),
            'summary': summary,
            'home': metadata.get_section('about').get('home', ''),
            'versions': ', '.join(versions),
            'license': metadata.get_section('about').get('license', ''),
            'recipe': ('https://github.com/bioconda/bioconda-recipes/tree/master/recipes/' +
                op.dirname(op.relpath(metadata.meta_path, RECIPE_DIR))),
            'notes': notes
        }
        readme = README_TEMPLATE.format(**template_options)
        # Write to file
        try:
            os.makedirs(op.join(OUTPUT_DIR, folder))  # exist_ok=True on Python 3
        except OSError:
            pass
        output_file = op.join(OUTPUT_DIR, folder, 'README.rst')
        with open(output_file, 'wb') as ofh:
            ofh.write(readme.encode('utf-8'))

    #wordcloud = WordCloud(max_font_size=40,
    #                      background_color='white',
    #                      stopwords=set(['package', 'tool'])).generate(" ".join(summaries))
    #plt.imshow(wordcloud)
    #plt.axis("off")
    #plt.savefig(op.join(BASE_DIR, 'wordcloud.png'), bbox_inches='tight')


if __name__ == '__main__':
    setup()
