# Accurial



## Notes

### Nix

- Install nix : `sh <(curl -L https://nixos.org/nix/install) --daemon`
- Run nix: `nix develop .`
- Update nix: `nix flake update`
- Finding if it's in a nix env `echo $IN_NIX_SHELL`


## Todo
- Pin the version for the different libs in flake.nix
- Check to have the same version of ruff everywhere
- Find a way to install psycopg2 (pg_config hell with nix)
- See to not have the .venv in the project with the docker
- Use profiles in the docker compose