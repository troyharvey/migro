from dataclasses import dataclass
import yaml
from migro import jinja


def get_output(profile=None):
    profiles = jinja.render_jinja_template('profiles.yml', env='production')
    profiles = yaml.safe_load(profiles)

    for profile_name, p in profiles.items():
        if profile and profile != profile_name:
            continue

        target = p['target']

        for output_key, output in p['outputs'].items():
            if len(p['outputs'].keys()) == 1 or target == output_key:
                return output
