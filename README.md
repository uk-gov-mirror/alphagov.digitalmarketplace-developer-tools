# Digital Marketplace developer tools

Common developer tooling for Digital Marketplace repos.

## Quickstart

Install [the digitalmarketplace-developer-tools package from PyPI][package] and
run Invoke in a Digital Marketplace repo to see what tasks are available:

```
$ pip install digitalmarketplace-developer-tools
$ invoke --list
```

## Stuff in this repo

### Invoke tasks

Developers on the Digital Marketplace need to be able to easily set-up a
developer environment for a repo, so they can quickly start making changes to
the code.

Traditionally this need has been met with `make`, however on the Digital
Marketplace we are starting to use [Invoke][pyinvoke] instead.

Invoke lets us write tasks once and use them for multiple repos. Being written
in Python, we can create a library of tasks and publish them on PyPI for reuse.
The [package for this repo][package] includes these tasks.

To start using the tasks in a repo, add a `tasks.py` file and import the
collection of tasks appropriate for the repo. For instance, for a frontend app:

```
# tasks.py
from dmdevtools.invoke_tasks import frontend_app_tasks as ns
```

The `as ns` part is needed so that the `invoke` command line tool sees the
imported tasks, read the [Invoke documentation on collections and
namespaces][1] for more details on how this works.

For backwards-compatibility, `make` can still be used for a repo. Just copy the
[`Makefile` from this repo](Makefile) (or just the `%` goal), and any
unrecognised goals will be sent to `invoke`.

[1]: http://docs.pyinvoke.org/en/stable/concepts/namespaces.html#starting-out

## Licence

Unless stated otherwise this codebase is released under [the MIT
License][licence]. This covers both the codebase and any sample code in the
documentation.

The documentation is [&copy; Crown copyright][copyright] and available under
the terms of the [Open Government 3.0][ogl] licence.

[licence]: LICENCE
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

[package]: https://pypi.org/project/digitalmarketplace-developer-tools
[pyinvoke]: pyinvoke.org
