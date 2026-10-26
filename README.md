# shippingwang / research

个人站 [`/research/`](https://shippingwang.com/research/) 的内容仓：短篇研究笔记、论文随想。

| 路径 | 说明 |
|------|------|
| `posts/*.md` | 正文（YAML front matter：`title` / `date` / `tags` / `summary`） |
| `build.py` | 生成静态站到 `dist/` |
| `static/` | CSS、站点壳 |

## 本地

```bash
python3 build.py
npx --yes serve dist
```

## 部署

由 [`shippingwang/site`](https://github.com/shippingwang/site) 的 `scripts/build.sh` 拉取本仓并写入 `dist/research/`。
