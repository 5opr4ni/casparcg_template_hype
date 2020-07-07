#!/usr/bin/python

# 	HypeExportPlayground.hype-export.py
#		Sample on implementing patches
#
#		MIT License
#		Copyright (c) 2020 Max Ziebell
#

import argparse
import json
import sys
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hype_version')
    parser.add_argument('--hype_build')

    parser.add_argument('--get_options', action='store_true')

    parser.add_argument('--modify_staging_path')
    parser.add_argument('--destination_path')
    parser.add_argument('--export_info_json_path')

    args, unknown = parser.parse_known_args()

    if args.get_options:
        def export_options():

            return {
                "exportShouldInlineHypeJS": False,
                "exportShouldInlineDocumentLoader": False,
                "exportShouldSaveHTMLFile": True,
                "exportShouldNameAsIndexDotHTML": False,
                # "indexTitle" : "",
                "exportShouldBustBrowserCaching": False,
                "exportShouldIncludeTextContents": False,
                "exportShouldIncludePIE": False,
                "exportSupportInternetExplorer6789": False,
                "exportShouldSaveRestorableDocument": False,
            }

        def save_options():
            return {
                "allows_export": True,
                "allows_preview": True,
            }

        options = {
            "export_options": export_options(),
            "save_options": save_options(),
            "min_hype_build_version": "596",
        }

        exit_with_result(options)

    elif args.modify_staging_path != None:
        import os
        import string
        import fnmatch
        import re

        export_info_file = open(args.export_info_json_path)
        export_info = json.loads(export_info_file.read())
        export_info_file.close()

        # common file globs
        glob_hype_runtime_minified = 'HYPE-'+args.hype_build+'*.min.js'

        # common hooks
        hook_api = '.API={'
        hook_props = 'top:{HYP_r'

        # patch helper
        def read_content(filepath):
            with open(filepath) as f:
                return f.read()

        def save_content(filepath, content):
            with open(filepath, "w") as f:
                f.write(content)

        def patch_pre_hook(hook, insert, filePattern):
            patch(hook, hook+insert, filePattern)

        def patch_post_hook(hook, insert, filePattern):
            patch(hook, insert+hook, filePattern)

        def patch(find, replace, filePattern):
            for path, dirs, files in os.walk(os.path.abspath(args.modify_staging_path)):
                for filename in fnmatch.filter(files, filePattern):
                    filepath = os.path.join(path, filename)
                    s = read_content(filepath)
                    s = s.replace(find, replace)
                    save_content(filepath, s)

        def read_runtime_content():
            for path, dirs, files in os.walk(os.path.abspath(args.modify_staging_path)):
                for filename in fnmatch.filter(files, glob_hype_runtime_minified):
                    return read_content(os.path.join(path, filename))

        runtime = read_runtime_content()

        # ADD PATCHES BELOW HERE

        import shutil
        shutil.rmtree(args.destination_path, ignore_errors=True)
        shutil.move(args.modify_staging_path, args.destination_path)

        exit_with_result(True)

# UTILITIES

# communicate info back to Hype


def exit_with_result(result):
    import sys
    print "===================="
    print json.dumps({"result": result})
    sys.exit(0)


if __name__ == "__main__":
    main()
