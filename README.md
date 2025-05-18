# Accurial



## Notes

### Nix

- install nix : `sh <(curl -L https://nixos.org/nix/install) --daemon`
- run nix: `nix develop .`
- update nix: `nix flake update`



## Todo
- Fix nix issue (no pg_config installed) => todo fix to be able to run the env without docker locally (for tests mostly) and have the venv elsewhere than there in the docker
- Pin the version for the different libs in flake.nix
- Check to have the same version of ruff everywhere