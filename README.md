# get-baseball-game-results

## Usage

### コンテナの起動

```
$ docker-compose up -d
```

### コンテナに入る

```
$ docker-compose exec python bash
```

### 実行

- 引数に試合日時を指定し、`main.py`を実行する

```
root@067fef3d3c7b:/work# python main.py 2020-11-11
```

### コンテナの停止・削除

```
$ docker-compose down
```
