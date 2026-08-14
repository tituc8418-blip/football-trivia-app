name: Build Football Trivia APK

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    name: Build Android APK
    runs-on: ubuntu-latest

    steps:
      - name: Get source code
        uses: actions/checkout@v4

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          workdir: .
          buildozer_version: stable
          command: buildozer android debug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: Football-Trivia-APK
          path: ${{ steps.buildozer.outputs.filename }}
