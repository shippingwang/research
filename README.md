# shippingwang / research

个人站 [`/research/`](https://shippingwang.com/research/) 的内容仓：短篇研究笔记、论文随想。

| 路径 | 说明 |
|------|------|
| `posts/*.md` | 正文（YAML front matter：`title` / `date` / `tags` / `summary`） |
| `build.py` | 生成静态站到 `dist/` |
| `static/` | CSS、站点壳 |

## 本地预览

```bash
python3 build.py
npx --yes serve dist
```

`build.py` **只写本仓 `dist/`**，不会动线上。线上 `/research/` 是 site CI 拉本仓再编进去的。

## 发布到 shippingwang.com

```bash
./publish.sh                 # 默认 commit 信息
./publish.sh "fix mercury note"
```

脚本会：`build.py` → commit/push **research** → 给 **site** 打空提交并 push（触发重新 clone research 部署）。

旁路 site 仓默认 `../site`；不在默认位置时：

```bash
SITE_DIR=/path/to/site ./publish.sh
```
