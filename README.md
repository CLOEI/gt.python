# gt.python

It's a cli multibot and it's cross platform. you can create the frontend if you like to. easily via websocket soon.

## Development
Requirements:
- C/C++ compiler (Clang, etc) ( Change CXX in Makefile if you use other than clang)
- Python 3.13
- Make
- Update the ENV VAR

Generate enet shared lib and install dependencies:
```bash
cp .env.example .env
make
make dev
```