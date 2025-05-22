import os
import xml.etree.ElementTree as ET
import plotly.express as px
from collections import defaultdict
from typing import List, Dict, Any
import pandas as pd

# Namespace mapping for LIDO
LIDO_NS = {'lido': 'http://www.lido-schema.org'}

def parse_xml_files(data_dir: str, max_files: int = -1) -> List[str]:
    """Recursively parse XML files in the given directory."""
    xml_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files[:max_files] if max_files != -1 else xml_files

def extract_data_from_xml(xml_file: str) -> Dict[str, List[str]]:
    """Extract artist info, materials, years, and subjects from <lido:subjectConcept>."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        data = {
            'nationalities': [],
            'subjects': [],
            'artwork_types': [],
            'artist_names': [],
            'artist_nationalities': [],
            'artist_roles': [],
            'art_materials': [],
            'years': [],
        }

        # Extract artist info, nationality, role, name
        for event_set in root.findall('.//lido:eventSet', LIDO_NS):
            for event in event_set.findall('lido:event', LIDO_NS):
                event_type = event.find('lido:eventType/lido:term', LIDO_NS)
                if event_type is not None and event_type.text.strip() == 'Production':
                    # Extract artist name
                    actor = event.find('lido:eventActor/lido:actorInRole/lido:actor', LIDO_NS)
                    if actor is not None:
                        name_actor_set = actor.find('lido:nameActorSet', LIDO_NS)
                        if name_actor_set is not None:
                            preferred_name = name_actor_set.find('lido:appellationValue[@lido:pref="preferred"]', LIDO_NS)
                            if preferred_name is not None:
                                data['artist_names'].append(preferred_name.text.strip())
                            else:
                                data['artist_names'].append('Unknown')

                        # Extract nationality
                        actor_id = actor.find('lido:actorID', LIDO_NS)
                        if actor_id is not None:
                            source = actor_id.get(f'{{{LIDO_NS["lido"]}}}source', '').lower()
                            if 'gnd' in source:
                                data['artist_nationalities'].append('Germany')
                            else:
                                data['artist_nationalities'].append('Unknown')
                        else:
                            data['artist_nationalities'].append('Unknown')

                        # Extract role
                        role_actor = event.find('lido:eventActor/lido:actorInRole/lido:roleActor/lido:term', LIDO_NS)
                        if role_actor is not None:
                            data['artist_roles'].append(role_actor.text.strip())
                        else:
                            data['artist_roles'].append('Unknown')

                    # Extract materials
                    event_materials = event.find('lido:eventMaterialsTech', LIDO_NS)
                    if event_materials is not None:
                        display_materials = event_materials.find('lido:displayMaterialsTech', LIDO_NS)
                        if display_materials is not None:
                            materials = [m.strip().lower() for m in display_materials.text.strip().split(';')]
                            data['art_materials'].extend(materials)
                        else:
                            data['art_materials'].append('Unknown')
                    else:
                        data['art_materials'].append('Unknown')

                    # Extract year
                    event_date = event.find('lido:eventDate/lido:date/lido:earliestDate', LIDO_NS)
                    if event_date is not None:
                        year = event_date.text.strip()
                        if len(year) >= 4:
                            data['years'].append(year[:4])
                        else:
                            data['years'].append('Unknown')
                    else:
                        data['years'].append('Unknown')

        # Extract subjects from <lido:subjectWrap> inside <lido:objectRelationWrap>
        for term in root.findall('.//lido:objectRelationWrap/lido:subjectWrap//lido:term', LIDO_NS):
            text = term.text.strip() if term.text else None
            if text:
                data['subjects'].append(text.lower())

        # Extract artwork type
        object_work_type = root.find('.//lido:objectWorkType/lido:term', LIDO_NS)
        if object_work_type is not None:
            artwork_type = object_work_type.text.strip()
            types = [t.strip().lower() for t in artwork_type.split(',')]
            data['artwork_types'].extend(types)

        return data
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse {xml_file}: {e}")
        return {k: [] for k in data}
    except Exception as e:
        print(f"[ERROR] Unexpected error in {xml_file}: {e}")
        return {k: [] for k in data}

def generate_histograms(data: Dict[str, List[str]], output_dir: str, show_count_one: bool = False) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for key in data:
        if data[key]:
            df_key = pd.DataFrame({key: data[key]})
            df_key = df_key.groupby(key).size().reset_index(name='count')

            # Filter out single-count entries if show_count_one is False
            if not show_count_one and key != 'years':
                df_key = df_key[df_key['count'] > 1]

            if key != 'years':
                df_key = df_key.sort_values(by='count', ascending=False)

            fig = px.bar(
                df_key,
                x=key,
                y='count',
                title=f'{key} Distribution',
                color_discrete_sequence=['orange']
            )

            # Save as PNG and HTML
            fig.write_image(os.path.join(output_dir, f'{key}_histogram.png'))
            print(f"Saved histogram: {key}_histogram.png")
            fig.write_html(os.path.join(output_dir, f'{key}_histogram.html'))
            print(f"Saved histogram: {key}_histogram.html")
            fig.show()

def main():
    data_dir = '../data/wien/lido'
    output_dir = '../output/01-initial-analysis'
    max_files = -1  # Change to a number to limit processing -1 is all
    show_count_one = False
    xml_files = parse_xml_files(data_dir, max_files)
    print(f"Found {len(xml_files)} XML files to process.")
    aggregated_data = {
        'nationalities': [],
        'subjects': [],
        'artwork_types': [],
        'artist_names': [],
        'artist_nationalities': [],
        'artist_roles': [],
        'art_materials': [],
        'years': [],
    }
    for idx, xml_file in enumerate(xml_files, 1):
        print(f"Processing file {idx} of {len(xml_files)}: {xml_file}...")
        try:
            file_data = extract_data_from_xml(xml_file)
            for key in aggregated_data:
                aggregated_data[key].extend(file_data.get(key, []))
        except Exception as e:
            print(f"[ERROR] Failed to process {xml_file}: {e}")
    print(f"Aggregated data from {len(xml_files)} files.")
    generate_histograms(aggregated_data, output_dir, show_count_one)

if __name__ == "__main__":
    main()