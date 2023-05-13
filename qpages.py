# Author: Kenny G Scott
# Date: 2023-05-10
# Description: A script to create new pages and the respective routes for Quasar projects
# Usage: python qpages.py
# Notes: This script is intended to be run from the root of the Quasar project

# Imports
import os
import re
from pathlib import Path
import sys
from typing import List

# Function to create the new page component
def create_page(page_name: str, page_type: str, pages_dir: Path, dynamic: bool):
    try:
        page_template = f"""<template>
  <q-page>
    <q-card>
      <q-card-section>
        <div class="text-h6">{page_name}</div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script{page_type}>
export default {{
  name: '{page_name}',
}};
</script>
"""
        with open(pages_dir / f"{page_name}.vue", "w") as f:
            f.write(page_template)
        return True
    except Exception as e:
        print(f"\033[91mError creating the page: {e}\033[0m")
        return False

# Utility function to convert a string to kebab-case
def to_kebab_case(s: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()

# Function to add the new routes
def add_route(page_names: List[str], route_paths: List[str], routes_file_path: Path, lang: str, dynamic: bool):
    try:
        with open(routes_file_path, "r") as f:
            content = f.readlines()

        if dynamic:
            route_lines = [
                f"{{ path: '{route_path}', component: () => import('pages/{page_name}.vue') }}," 
                for page_name, route_path in zip(page_names, route_paths)
            ]
        else:
            route_lines = [
                f"{{ path: '{route_path}', component: {page_name} }}," 
                for page_name, route_path in zip( page_names, route_paths)
            ]
            import_lines = [
                f"import {page_name} from 'pages/{page_name}.vue';\n" 
                for page_name in page_names
            ]
            
            content[:0] = import_lines

        # Find the index of the line containing "path: '/'"
        main_layout_index = next(
            (i for i, line in enumerate(content) if "path: '/'" in line),
            None
        )

        if main_layout_index is not None:
            # Find the index of the "children: [" line
            children_start_index = next((i for i, line in enumerate(
                content[main_layout_index:], start=main_layout_index) if "children: [" in line), None)

            if children_start_index is not None:
                # Find the index of the closing "]" of the "children" array
                children_end_index = next((i for i, line in enumerate(
                    content[children_start_index:], start=children_start_index) if "]" in line), None)

                if children_end_index is not None:
                    # Check if the previous line is missing a comma
                    if not content[children_end_index - 1].strip().endswith(','):
                        content[children_end_index - 1] = content[children_end_index - 1].rstrip() + ',\n'

                    # Insert the new routes
                    content[children_end_index:children_end_index] = [
                        f"      {route_line}\n" for route_line in route_lines]

        with open(routes_file_path, "w") as f:
            f.writelines(''.join(content))
        return True
    except Exception as e:
        print(f"\033[91mError adding the route: {e}\033[0m")
        return False


def main():
    page_names = []
    route_paths = []

    while True:
        # Prompt user for input
        page_name = input("Enter page name: ").strip()
        route_path = input(
            "Enter the route path (leave blank to use page name): ").strip()

        if not route_path:
            route_path = to_kebab_case(page_name)

        lang = input("Enter the script type (js or ts): ").lower().strip()
        if lang not in ["js", "ts"]:
            print(
                "\033[91mError: Invalid script type entered. Please enter 'js' or 'ts'.\033[0m")
            sys.exit(1)

        dynamic = input(
            "Do you want to use dynamic component loading? (y/n): ").lower().strip()
        if dynamic in ['y', 'yes']:
            dynamic = True
        else:
            dynamic = False

        page_names.append(page_name)
        route_paths.append(route_path)

        add_more = input(
            "Do you want to add more pages? (y/n): ").lower().strip()
        if add_more in ['n', 'no']:
            break

    # Search for the "pages" directory
    pages_dir = None
    for root, _, _ in os.walk("."):
        if root.endswith("/pages"):
            pages_dir = Path(root)
            break

    if not pages_dir:
        print("\033[91mError: 'pages' directory not found.\033[0m")
        sys.exit(1)

    # Create the new pages
    created_pages = []
    for page_name in page_names:
        page_type = " lang='ts'" if lang == "ts" else ""
        if create_page(page_name, page_type, pages_dir, dynamic):
            created_pages.append(page_name)

    # Search for the routes file
    routes_file = "routes.ts" if lang == "ts" else "routes.js"
    routes_file_path = None
    for root, _, files in os.walk("."):
        if routes_file in files:
            routes_file_path = Path(root) / routes_file
            break

    if not routes_file_path:
        print(f"\033[91mError: '{routes_file}' file not found.\033[0m")
        sys.exit(1)

    # Add the routes
    if add_route(created_pages, route_paths, routes_file_path, lang, dynamic):
        print(
            f"\033[92mSuccessfully created pages: {', '.join(created_pages)}\033[0m")

if __name__ == "__main__":
    main()
