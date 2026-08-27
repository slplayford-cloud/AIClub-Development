# aiclub

Command-line tool for the university **AI & Machine Learning club**. Members use it to
verify their membership with a university email, browse assignments and workshops, and
submit their code. There is no automated grading — submissions are stored for officers
to review in the Supabase dashboard.

## Install (members)

Requires [uv](https://docs.astral.sh/uv/): 

How to install uv package manager:

macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```


```bash
uv tool install "git+https://github.com/slplayford-cloud/AIClub-Development#subdirectory=cli-client"
```

Then:

```bash
aiclub status                   # check the connection
aiclub login                    # sign in with your @nd.edu Google account (M1)
aiclub whoami                   # show who you're logged in as             (M1)
aiclub update                   # update aiclub to the latest version
aiclub assignments list         # browse assignments                       (M2)
aiclub submit hw1 ./solution.py # submit a file or folder                  (M3)
```

## Develop

```bash
cd cli-client
uv sync                         # create the venv + install deps
uv run aiclub status            # run without installing
uv run pytest                   # run tests
```

### Configuration

```toml
supabase_url = "https://<project>.supabase.co"
supabase_anon_key = "<anon-key>"
allowed_domain = "university.edu"
```

## Status

Built in weekend-sized milestones:

- [x] **M0** — Project scaffold + Supabase connection (`aiclub status`)
- [ ] **M1** — Account setup via Google sign-in (`login`, `whoami`, `logout`) — see [docs/AUTH_SETUP.md](docs/AUTH_SETUP.md)
- [ ] **M2** — Browse assignments & workshops
- [ ] **M3** — Code submission
