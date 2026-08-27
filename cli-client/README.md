# aiclub

Command-line tool for the university **AI & Machine Learning club**. Members use it to
verify their membership with a university email, browse assignments and workshops, and
submit their code. There is no automated grading — submissions are stored for officers
to review in the Supabase dashboard.

## Install (members)

Requires [uv](https://docs.astral.sh/uv/) — one tool, no separate Python setup:

```bash
uv tool install aiclub          # once published
# or, from a checkout of this repo:
uv tool install ./cli-client
```

Then:

```bash
aiclub status                   # check the connection
aiclub login you@university.edu # verify with an emailed code   (M1)
aiclub assignments list         # browse assignments            (M2)
aiclub submit hw1 ./solution.py # submit a file or folder       (M3)
```

## Develop

```bash
cd cli-client
uv sync                         # create the venv + install deps
uv run aiclub status            # run without installing
uv run pytest                   # run tests
```

### Configuration

The Supabase URL, anon key, and allowed email domain are club-wide constants baked
into the package (the anon key is public by design). For local development you can
override them with environment variables:

```bash
export AICLUB_SUPABASE_URL=https://<project>.supabase.co
export AICLUB_SUPABASE_ANON_KEY=<anon-key>
export AICLUB_ALLOWED_DOMAIN=university.edu
```

…or in `~/.config/aiclub/config.toml`:

```toml
supabase_url = "https://<project>.supabase.co"
supabase_anon_key = "<anon-key>"
allowed_domain = "university.edu"
```

## Status

Built in weekend-sized milestones:

- [x] **M0** — Project scaffold + Supabase connection (`aiclub status`)
- [ ] **M1** — Account setup & email verification (`login`, `whoami`, `logout`)
- [ ] **M2** — Browse assignments & workshops
- [ ] **M3** — Code submission
