---
name: staged-simplifier
description: 編集後のファイルに処理の複雑化がないか確認し、必要であれば修正を行う。実装作業後に品質担保の目的で使用する。また「/staged-simplifier」で呼び出されたときに使用する。
context: fork
agent: code-simplifier
disable-model-invocation: true
---

直近に編集したPythonファイルについて、処理が複雑化している部分がないか確認し、必要であれば修正を行ってください。