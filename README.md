# cal-helper

> [!WARNING]
> **cal-helper** has been archived in favor of the
> [Cal's cals admin panel](https://github.com/olillin/cals-cals-admin).

Helper to scrape news and events from chalmers.it.

## Installation on NixOS

Below is an example of how to add the flake input and install the package:

`flake.nix`

```nix
{
  description = "NixOS configuration with cal-helper";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-25.11";

    cal-helper = {
      url = "github:olillin/cal-helper";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    cal-helper,
    ...
  } @ inputs: let
    system = "your system";
  in {
    nixosConfigurations.yourconfiguration = nixpkgs.lib.nixosSystem {
      specialArgs = {inherit inputs;};
      modules = [
        {
          environment.defaultPackages = [
            cal-helper.packages.${system}
          ];
        }
        # Other modules
        ./configuration.nix
      ];
    };
  };
}
```

