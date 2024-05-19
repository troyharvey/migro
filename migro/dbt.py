import os
import yaml
from migro import jinja


def _get_profiles_path():
    """
    dbt best practice is to store the profiles.yml file in the ~/.dbt directory.
    But it's common to store the profiles.yml file in the root of the dbt project.
    migro checks the local project directory and then checks the .dbt home directory.
    Return the path to the profiles.yml file.
    """

    if os.path.isfile("./profiles.yml"):
        return "./profiles.yml"
    elif os.path.isfile("~/.dbt/profiles.yml"):
        return "~/.dbt/profiles.yml"
    else:
        raise Exception("Missing dbt profiles.yml")


def _profiles_yaml_to_dict(profiles_path):
    """
    Render the profiles.yml file using jinja.
    Return the rendered profiles.yml file as a dictionary.
    """

    profiles_yaml: str = jinja.render_jinja_template(profiles_path)
    return yaml.safe_load(profiles_yaml)


def _get_profile(profiles: dict, profile_name: str = None) -> dict:
    """
    Return the target dbt profile from a list of profiles.
    """

    for key, profile in profiles.items():
        # Return the first profile when no profile_name is specified.
        if profile_name is None:
            return profile

        if key == profile_name:
            return profile

    raise Exception(f"Profile {profile_name} not found in profiles.yml")


def _get_output(profile: dict, target: str = None) -> dict:
    """
    Return the target dbt output from a profile.
    """

    if not target:
        target = profile.get("target")

    assert target is not None, "No target specified"

    for output_name, output in profile["outputs"].items():
        if target != output_name:
            continue
        return output

    raise Exception(f"Target {target} not found in profiles.yml")


def get_target_output(profile_name: str = None, target=None) -> dict:
    """
    Get the target output database configuration from the dbt profiles.yml file.
    """

    profiles_path = _get_profiles_path()
    profiles = _profiles_yaml_to_dict(profiles_path)
    profile = _get_profile(profiles, profile_name)
    return _get_output(profile, target)
