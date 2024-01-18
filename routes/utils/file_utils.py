from typing import Tuple


def replace_placeholder_env_values_with_user(user_env: dict, user_id: str) -> Tuple[str, str]:
    """
    Replace placeholder values in .env file with user values

    :param user_env: User environment values
    :param user_id:
    :return: (Updated Dockerfile-<user_id> path, Updated .<user_id>-env file path)
    """
    files_prefix = 'routes/utils/files'
    with open(f'{files_prefix}/.user-env', 'r') as f:
        env = f.read()

    env = env.replace('<USER-ID>', user_id)
    for key, value in user_env.items():
        env = env.replace(key, value)

    env_file_name = f'.{user_id}-env'
    user_env_fp = f'{files_prefix}/{env_file_name}'
    with open(user_env_fp, 'w') as f:
        f.write(env)

    with open(f'{files_prefix}/Dockerfile-User-Base', 'r') as f:
        dockerfile = f.read()

    user_dockerfile = dockerfile.replace('<USER-ENV>', env_file_name)
    user_dockerfile_name = f'Dockerfile-{user_id}'
    user_dockerfile_fp = f'{files_prefix}/{user_dockerfile_name}'
    with open(user_dockerfile_fp, 'w') as f:
        f.write(user_dockerfile)

    return user_dockerfile_fp, user_env_fp
