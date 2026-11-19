# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [所有语言](#语言)

**Home Assistant 的飞机，显示在一张地图上。** Live Track Aircraft 把飞过你家上空的飞机，或飞过你选择的世界任何地方的飞机，显示在你的 Home Assistant 地图上：每架飞机都画成它自己的机型，朝向它飞行的方向，标出谁在运营它，并在已知时标出它飞往哪里。它还能跟踪选定的飞机和航班，无论它们在哪里，并在你指定的区域内留意军用飞机。

> **Live Track Aircraft 是 Live Track 的一个模块**。Live Track 是一组 Home Assistant 集成，把一切移动的东西以及它们穿过的天气画在同一张共享地图上：飞机、船只、火车和天气。可以单独安装，也可以和其他模块一起安装（[见下方列表](#live-track-的组成部分其他模块)）。

> **正在成长，欢迎提出想法。** Live Track Aircraft 目前覆盖志愿者运行接收机的全世界，美国的航线和所有者名称最详细。我们正在添加更多航线来源和飞机信息。缺少你那里的吗？[提出建议](#帮助它成长)，或者自己添加：我们会帮你完成。

**状态：0.1.1，已发布。** 可通过链接添加到 Marketplace（[见下文](#安装步骤)）；它还不在 Marketplace 的目录中。

StrausbergAutomationWorks 的原创作品。与 adsb.fi、adsb.lol、adsbdb、美国联邦航空管理局（Federal Aviation Administration，FAA）、OurAirports、ADS-B Radar、任何航空公司或任何飞机运营者均无关联，也未获得它们的认可。

> ⚠ **这不是安全系统。** 它显示公开数据，通常延迟几秒，有时一分钟或更久，而且只显示志愿者的接收机恰好收到的飞机。它不能用于导航、飞机间隔或任何其他操作用途。

---

## 目录

1. [全部功能](#全部功能)
2. [适用地区](#适用地区)
3. [Live Track 的组成部分：其他模块](#live-track-的组成部分其他模块)
4. [开始之前](#开始之前)
5. [安装步骤](#安装步骤)
6. [设置步骤](#设置步骤)
7. [解锁更多功能的免费密钥](#解锁更多功能的免费密钥)
8. [把地图放到仪表盘上](#把地图放到仪表盘上)
9. [在自动化中使用](#在自动化中使用)
10. [地图上的全部内容详解](#地图上的全部内容详解)
11. [它创建的全部实体](#它创建的全部实体)
12. [它发送和下载的内容](#它发送和下载的内容)
13. [帮助它成长](#帮助它成长)
14. [语言](#语言)
15. [致谢与许可](#致谢与许可)
16. [关键词](#关键词)

---

## 全部功能

### 在地图上，无需任何设置

你添加一个**区域**：地图上的一个中心点和围绕它的半径。它从你的家开始。下面的一切都会出现在这个区域内，或者在表格注明的情况下，出现在世界任何地方。

| 内容 | 范围 | 来源 |
|---|---|---|
| **飞机**：客机、轻型飞机、直升机、滑翔机、热气球和无人机，每架都画成它自己的机型，并朝向它飞行的方向 | 每个区域内 | adsb.fi，adsb.fi 没有响应时用 adsb.lol |
| **谁在运营它**：航空公司、所有者，或在不知道其他信息时显示机型，显示在标记的标签上 | 每架飞机 | 航空公司的呼号；所有者来自 FAA 航空器登记册（美国） |
| **表示谁在飞的颜色**：政府、警察、联邦执法机构、军队、空中救护和直升机，各有自己的颜色 | 每架已知的飞机 | FAA 航空器登记册（美国）和数据源的军用标志 |
| **航线**：飞机从哪里起飞、飞往哪里，带机场名称和预计到达时间 | 向 FAA（美国）提交飞行计划的航班；在其他地方，adsbdb 知道该航班时 | FiledRoutesDB，然后是 adsbdb |
| **美国总统的飞机**，以及第 89 空运联队（89th Airlift Wing）的飞机和护航它们的军用飞机 | 全世界任何地方 | adsb.fi 及其军用飞机列表 |
| **公开的 EnforcementAircraft 列表上的飞机**（移民和联邦执法），带闪烁的灯光 | 每个区域内 | EnforcementAircraft 列表 |
| **你的监视区域内的军用飞机**：数据源标记为军用的每架飞机，在你指定的最多十个圆圈内，即使你的区域已满也会显示。可选：你在设置对话框中输入这些圆圈 | 全世界任何地方 | adsb.fi 的军用飞机列表 |
| **你关注的飞机和航班**：你自己的飞机、一个俱乐部的机队，或家人正在乘坐的航班。可选：你在设置对话框中输入它们的代码 | 全世界任何地方 | adsb.fi |
| **为某架飞机使用你自己的图片**，代替它的图标 | 这架飞机显示的任何地方 | 你放进一个文件夹的图片（[方法](#为某架飞机使用你自己的图片)） |

### 用你自己的免费密钥或账户开启

| 免费密钥或账户 | 增加什么 |
|---|---|
| **adsb.lol** 密钥 | 每天向第二个来源 adsb.lol 发送更多请求，这样在 adsb.fi 长时间中断时地图仍能继续工作 |

每个都只需几分钟就能获得：[见下方的分步说明](#解锁更多功能的免费密钥)。

---

## 适用地区

| 地区 | 你能得到什么 | 来源 | 需要 |
|---|---|---|---|
| **全世界** | 有志愿者运行接收机的地方的飞机位置：欧洲和北美上空密集，其他地方较稀疏，远海上很少或没有 | adsb.fi、adsb.lol | 无 |
| **全世界** | 航线上的机场名称，以及用于计算到达时间的机场时区 | OurAirports，通过 AirportZones 表 | 无 |
| **全世界** | 许多航空公司航班的航线，并与飞机的实际位置进行核对 | adsbdb | 无 |
| **北美**：美国 | 在美国注册的飞机的所有者和运营者名称，以及政府和警察飞机的颜色 | FAA 航空器登记册 | 无 |
| **北美**：美国 | 向 FAA 提交的航班的航线，包括往返美国的国际航班 | FiledRoutesDB | 无 |

不在列表中？[告诉我们](#帮助它成长)。只要有人公开发布数据，我们就会考虑添加。

⚠ **有接收机的地方覆盖良好，没有接收机的地方就没有覆盖。** 只有当志愿者的接收机收到一架飞机，或几台接收机一起能确定它的位置时，它才会出现。任何设置都无法创造不存在的覆盖。**地图上的天空是空的，可能意味着你附近没有接收机，而不是没有飞机。**

⚠ **航线主要适用于美国。** FiledRoutesDB 只包含向 FAA 提交的飞行计划。在其他地方，航线来自 adsbdb，它知道许多航空公司航班，但很少知道其他航班，所以在美国以外，许多飞机不显示航线。

⚠ **所有者名称只适用于在美国注册的飞机。** 在其他国家注册的飞机显示根据呼号得出的航空公司，或者显示它的机型。

---

## Live Track 的组成部分：其他模块

Live Track 是一组 Home Assistant 集成，每种移动的东西一个，全部画在同一张地图卡片上。每个都能单独工作；合在一起就成为一幅实时画面。它们共享地图卡片和一个 Python 库（[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)），因此再安装一个模块不会向另一个模块已在读取的来源增加请求。

| 模块 | 在地图上显示什么 | 状态 |
|---|---|---|
| **Live Track Aircraft** | 通过 ADS-B 显示头顶的飞机，带航线和机型图标（本模块） | 已发布 |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | 通过 AIS 显示船只和船艇，在你附近或任何地方 | 已发布 |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | 北美、欧洲和澳大利亚的通勤列车 | 已发布 |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | 北美、欧洲和澳大利亚的城际和长途列车 | 已发布 |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | 来自公开列表的移民和联邦执法飞机及船只 | 已发布 |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | 天气、风暴和自然灾害 | 已发布 |
| Live Track Stations | 每个车站的发车信息板和"该出发了"提醒 | 计划中 |
| Live Track Satellites | 从头顶经过的卫星 | 计划中 |
| Live Track Freight Trains | 铁路公开发布的货运和工程列车 | 计划中 |
| Live Track Transit | 城市公交、有轨电车、渡轮和地铁 | 计划中 |
| Live Track Intercity Buses | 城际和区域长途客车 | 计划中 |
| Live Track Commuter Buses | 通勤巴士 | 计划中 |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | 每个模块都在上面绘制的共享地图卡片 | 已发布，随每个模块一起安装 |

一切都是免费和开源的。没有任何功能只留给赞助者。

---

## 开始之前

* **Home Assistant** 2026.11 或更高版本。
* 你的 Home Assistant 中的 **Marketplace**（HACS），用来方便地安装和更新。没有它，你也可以手动复制文件。
* Home Assistant 需要**互联网访问**：一切都来自公开来源。
* **可选：Marketplace 中的 auto-entities**，用来把标记放到地图上（见[把地图放到仪表盘上](#把地图放到仪表盘上)）。
* 无需付费，也不需要账户。上面的 adsb.lol 密钥是可选的。
* 集成第一次加载时，Home Assistant 会自动安装它需要的两个 Python 包（`saw-livetrack` 和 `tzfpy`）。

---

## 安装步骤

### 通过 Marketplace（推荐）

Live Track Aircraft 还不在 Marketplace 的目录中。通过它的链接添加：

1. 在 Home Assistant 中打开 **设置 → Marketplace**（HACS）。
2. 选择 **从链接添加**（或三点菜单 → **自定义存储库**）。
3. 输入 `StrausbergAutomationWorks/LiveTrackAircraft`。如果询问类型，选择 **集成**。
4. 在列表中找到 **Live Track Aircraft**，选择 **下载** 或 **安装**。
5. **重启 Home Assistant**：**设置 → 系统 → 修复** 会提供重启，或使用 **设置 → 系统 → 重启**。

之后，Marketplace 会把每个新版本作为更新提供给你。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest)的源代码。
2. 把其中的 `custom_components/live_track_aircraft` 文件夹复制到 Home Assistant 配置文件夹中的 `custom_components` 文件夹（如果没有 `custom_components`，请创建它）。
3. 重启 Home Assistant。

要手动更新，用新版本的文件夹替换旧文件夹，然后重启。

---

## 设置步骤

设置对话框是英文的。这里按对话框显示的名称列出它的字段。

1. 打开 **设置 → 设备与服务**。
2. 选择 **添加集成**（右下角），搜索 **Live Track Aircraft**。
3. **Centre**（中心点）：把标记拖到你想观察的天空的中心。它从你的家开始。
4. **Radius (km)**（半径，公里）：显示离中心多远的飞机，1 到 463 公里（0.6 到 288 英里）。如果不确定，保留 56 公里（35 英里）。
5. **Update interval (seconds)**（更新间隔，秒）：保留 15。来源会拒绝更频繁的请求。
6. **Maximum aircraft published**（最多发布的飞机数）：保留 250。这是一个安全上限，不是用来少显示飞机的方法。
7. 四个可选字段暂时留空。下面会逐一说明。
8. 选择 **提交**。

就这样。飞机会在一分钟内出现。每个区域是一个条目，以它的中心点和半径为标题，例如 `39.817, -84.050 - 56 km`。要观察第二个区域，用另一个中心点或半径再次添加这个集成。相同的中心点和半径添加两次会被拒绝。

航线、机场名称和所有者名称会在最初几分钟内随着它们所需的文件下载完毕而逐渐出现（[它发送和下载的内容](#它发送和下载的内容)）。

### 更改显示内容：选项

在你要更改的区域上打开 **设置 → 设备与服务 → Live Track Aircraft → 配置**（齿轮图标）。每个选项的通俗说明：

| 选项 | 作用 | 默认值 |
|---|---|---|
| **Centre** | 移动区域；它的标题随之改变 | 你的家 |
| **Radius (km)** | 显示离中心多远的飞机，1 到 463 公里（0.6 到 288 英里） | 56 公里（35 英里） |
| **Update interval (seconds)** | 多久请求一次位置，15 到 3,600 秒 | 15 |
| **Maximum aircraft published** | 安全上限，1 到 1,000；圆圈内的飞机更多时，保留最近的。你关注的飞机、你的军用监视区域内的飞机和 EnforcementAircraft 列表上的飞机总是保留 | 250 |
| **Military watch areas** | 显示每架军用飞机的圆圈（[方法](#军用监视区域)） | 空 |
| **Aircraft to follow (hex codes)** | 按十六进制代码在任何地方跟踪的飞机（[方法](#你关注的飞机和航班)） | 空 |
| **Flights to follow (call signs)** | 按呼号在任何地方跟踪的航班（同一节） | 空 |
| **adsb.lol API key** | 你自己的 adsb.lol 密钥（[如何获取](#解锁更多功能的免费密钥)） | 空 |

清空四个可选字段中的一个，即可关闭那一部分。

---

## 解锁更多功能的免费密钥

这些都是免费的个人密钥：每个安装 Live Track Aircraft 的人都获取自己的密钥。把每个密钥粘贴到 **设置 → 设备与服务 → Live Track Aircraft → 配置** 中。

### adsb.lol（向第二个来源发送更多请求，全世界）

Live Track Aircraft 先询问 adsb.fi，只有在 adsb.fi 没有响应时才询问 adsb.lol。没有密钥时，adsb.lol 每天允许一个互联网地址发出 500 个请求，adsb.fi 中断时大约两小时就会用完。密钥可以提高这个上限。开始使用时不需要密钥。

1. 打开 <https://www.adsb.lol/request>，用那里的表单申请一个免费密钥。adsb.lol 的文档说明这种密钥每天可发出 1,000 个请求。
2. 如果你用自己的接收机向 adsb.lol 提供数据，请改用你的数据提供者（feeder）密钥：adsb.lol 的文档说明它每天可发出 7,200 个请求。你的密钥在 adsb.lol 的 **My keys** 下（<https://www.adsb.lol/mmb>）。
3. 把密钥粘贴到 **adsb.lol API key** 中，然后选择 **提交**。

密钥只发送给 adsb.lol。如果 adsb.lol 拒绝它（错误或已过期），Live Track Aircraft 会在没有密钥的情况下继续工作，该区域的 `sensor.aircraft_in_range` 会在 `adsblol_key` 属性中显示 `refused`，直到你更改密钥。否则显示 `set`，没有密钥时显示 `none`。不需要密码，也不需要任何秘密信息。

---

## 把地图放到仪表盘上

地图是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，每个 Live Track 模块都在这张卡片上绘制。**它随 Live Track Aircraft 一起安装**：无需下载，无需复制，也无需添加资源。

1. 打开一个仪表盘，选择铅笔图标（**编辑仪表盘**），然后选择 **添加卡片**。
2. 滚动到最下面，选择 **手动**。
3. 粘贴下面的内容，然后选择 **保存**：

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_aircraft
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

标记需要 Marketplace 中的 [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)。如果安装了其他 Live Track 模块，为它们的每个来源再添加一个 `- domain: geo_location` 过滤器（`live_track_ships`、`live_track_weather` 等）。

**在地图上：**

* 每架飞机都画成它自己的机型，朝向它飞行的方向，并在它报告的位置之间平滑移动。
* 它的标签是航班的呼号（`UAL308`），否则是运营者（`Lewis University`），再否则是机型（`Cessna 172 Skyhawk`）。
* 把指针**指向**一架飞机，可以看到它的航空公司或运营者，在已知航线时还能看到航线和距离到达还有多少分钟。**点击**它可以看到全部详情。

如果你的仪表盘资源是用 YAML 设置的（`lovelace: resource_mode: yaml`），就无法替你自动注册：这时 **修复** 中会出现一个问题，给出需要添加的确切行。你自己通过 Marketplace 安装的卡片不会被改动。如果在区域仍然设置着的情况下删除了集成的文件，而且没有安装其他 Live Track 模块，请自己在 **设置 → 仪表盘 → 资源** 中删除卡片的那一行。任何其他显示 `geo_location` 实体的地图卡片也会显示这些飞机，只是显示为普通标记。

---

## 在自动化中使用

一切都是普通的 Home Assistant 实体，所以自动化编辑器可以直接使用它们，无需代码。

**当一架军用飞机进入你的某个军用监视区域时，向手机发送通知：**

1. **设置 → 自动化与场景 → 创建自动化 → 创建新的自动化**。
2. **每当**：**添加触发条件** → **实体** → **数值状态**。选择实体 **Aircraft in range**，**属性** 选择 **Military in areas**（`military_in_areas`），**高于** 填 `0`。
3. **就执行**：**添加动作**，搜索你手机的通知动作（它带有你手机的名称），然后输入一条消息，例如：

   ```text
   一架军用飞机进入了你的监视区域
   ```

4. **保存**。

这需要至少一个军用监视区域（[方法](#军用监视区域)）。

**其他想法：** 家人的航班在空中时发送通知，依据是 `followed_found` 属性升到 0 以上；当你在法兰克福（德国）的家上空有超过 20 架飞机时开灯；用 `sensor.aircraft_in_range` 在仪表盘上显示你在昆士兰（澳大利亚）的机场上空的飞机数量；当你俱乐部的飞机起飞、它自己的实体（`geo_location.aircraft_` 加上它的十六进制代码）出现时发送消息。

---

## 地图上的全部内容详解

### 飞机

飞机通过无线电发送自己的位置，这种系统叫作 ADS-B。世界各地的志愿者运行接收机，并通过社区网络分享他们收到的数据。Live Track Aircraft 默认每 15 秒向其中一个网络 adsb.fi 询问你圆圈内的每架飞机。当 adsb.fi 没有响应，或者返回的飞机比片刻之前少得多时，它会询问 adsb.lol。当几台接收机都收到一架不发送自身位置的飞机时，网络仍然可以确定它的位置（多点定位，MLAT）。

每架飞机是一个标记，以它的十六进制代码命名：这是它的应答机发送的六个字符的地址，属于这架飞机，不会改变。飞机进入你的圆圈时标记出现，离开时标记被移除。

标签显示已知的最有用的名称，顺序如下：

| 飞机有 | 标签显示 | 示例 |
|---|---|---|
| 航班的呼号 | 呼号 | `UAL308` |
| 否则，已知的运营者 | 运营者 | `Lewis University` |
| 否则，已知的机型 | 机型 | `Cessna 172 Skyhawk` |
| 以上都没有 | 注册号、机型代码或十六进制代码 | `N12345` |

⚠ 不显示：地面上的飞机、机场车辆，以及没有身份信息的纯雷达航迹。不发送信号的飞机，或者在没有接收机能收到的地方飞行的飞机，无法显示。

每架飞机上的属性：`identity`（十六进制代码）、`callsign`、`registration`、`aircraft_type`、`aircraft_name`、`operator`、`altitude_m`、`speed_kmh`、`vertical_rate_ms`、`course_deg`、`squawk`、`emitter_category`、`is_military`、`is_government`、`last_seen`。

### 颜色和图标

每架飞机都画成它自己的机型：客机、公务机、单发轻型飞机、双发飞机、直升机、倾转旋翼机、滑翔机、热气球、无人机等等，大小按它的类别缩放。螺旋桨和旋翼会转动。图标朝向飞机飞行的方向；慢速飞机保持它最后的方向，而不会原地打转。

在已知的情况下，颜色表示谁在飞它：

| 颜色 | 谁 |
|---|---|
| 浅灰色 | 大多数飞机 |
| 薄荷绿 | 直升机和其他旋翼航空器 |
| 琥珀色 | 政府飞机和空中救护 |
| 蓝色 | 联邦执法机构 |
| 军绿色 | 军队和海岸警卫队 |
| 白色，带闪烁的蓝灯 | 警察 |
| 闪烁的红灯和蓝灯 | EnforcementAircraft 列表上的飞机（[见下文](#enforcementaircraft-列表与-live-track-salt)） |
| 持续的光晕 | 执飞 ICE Air 包机（以及其他业务）的客机 |

⚠ 飞机的所有者主要只对在美国注册的飞机已知，来自 FAA 登记册。在其他地方，颜色只来自数据源的军用标志和飞机的机型。

### 航线和到达时间

航线显示飞机从哪里起飞、飞往哪里，带两个机场的名称，以及预计到达时间。它来自两个地方：

1. **FiledRoutesDB**，一个向 FAA（美国）提交的飞行计划的公开文件，由 StrausbergAutomationWorks 构建和发布，每天下载一次。每条航线都会与飞机的位置和飞行方向进行核对。不吻合的航线仍会显示，并在 `route_check` 中标记为不吻合。
2. **adsbdb**，只在 FiledRoutesDB 没有该呼号的航线时询问，每个呼号询问一次。只有当它的答复与飞机的实际位置吻合时才会显示。

所有者要求 FAA 不公开显示其航班的飞机（FAA 的 LADD 列表，Limiting Aircraft Data Displayed）在 FiledRoutesDB 发布前就已被移除。当文件过期，或者构建它所用的 LADD 列表超过 14 天时，Live Track Aircraft 会删除它的副本，因此它永远不会显示按旧列表过滤的航线。

到达时间是估算，不是时刻表：剩余的直线距离，飞机巡航时按它的速度计算，不在巡航时按它所属类别的典型速度计算。等待、进近和滑行不计算在内。

每架有航线的飞机上的属性：`origin_icao`、`destination_icao`、`origin_name`、`destination_name`、`route_source`、`route_check`、`arrival_estimated_at`。

### 军用监视区域

在你选择的圆圈内、世界任何地方，数据源标记为军用的每架飞机，即使你的区域已满也会显示。

1. 在一个区域上打开 **设置 → 设备与服务 → Live Track Aircraft → 配置**。
2. 在 **Military watch areas** 中，把每个圆圈写成 `latitude,longitude,km`（纬度、经度、公里），圆圈之间用分号分隔，例如 `39.81,-84.04,150; 34.0,-117.8,463`。最多十个圆圈，每个 1 到 2,000 公里（0.6 到 1,243 英里）。
3. 选择 **提交**。

圆圈内的军用飞机会在一分钟内出现，并每分钟移动一次。每架都带有 `watch: military area`。该区域的 `sensor.aircraft_in_range` 在 `military_in_areas` 中统计它们的数量，并在 `military_by_area` 中按圆圈统计。清空该字段即可停止。

⚠ 它只显示发送信号并被标记为军用的飞机。军用航班可以关闭应答机飞行，而使用民用注册号的军用飞机不会被标记。

### 你关注的飞机和航班

Live Track Aircraft 可以跟踪你选择的飞机，无论它们在世界的哪里，而不只是在你的圆圈内：你自己的飞机、一个俱乐部或公司的机队，或家人正在乘坐的航班。

1. 在你希望它们与之一起显示的区域上打开 **设置 → 设备与服务 → Live Track Aircraft → 配置**。
2. 填写 **Aircraft to follow (hex codes)**（要跟踪的飞机，十六进制代码）、**Flights to follow (call signs)**（要跟踪的航班，呼号），或两者都填。
3. 选择 **提交**。它们会在大约一分钟内出现。

**每架飞机一个代码就够了。** 按你想跟踪的对象选择：

| 要跟踪 | 使用 | 示例 |
|---|---|---|
| 一架飞机，无论它执飞哪个航班（你自己的飞机、一个机队） | 它的**十六进制代码** | `a1b2c3` |
| 一个航班，无论由哪架飞机执飞（家人的行程） | 它的**呼号** | `UAL1234` |

为同一架飞机同时输入两种代码没有害处（它只画一次），但也没有任何好处。

**输入代码：**

* 用逗号分隔代码：`a1b2c3, a4b5c6, a7b8c9`。代码之间用空格或分号也可以。
* 十六进制代码正好六个字符：数字 0 到 9 和字母 a 到 f，大小写均可。
* 呼号是 2 到 8 个字母和数字，按飞机发送的样子输入，不带空格或连字符：`UAL1234`，而不是 `UA 1234` 或 `UAL-1234`。
* 最多 100 个十六进制代码和 100 个呼号。输入两次的代码只算一次。
* 如果某个代码有误，对话框会拒绝该字段，说明正确的代码是什么样子，并且在改正之前不保存任何内容。

**查找代码。** 地图上的每架飞机都在 `identity` 属性中带有它的十六进制代码，在 `callsign` 属性中带有它的呼号。对于在美国注册的飞机，FAA 登记册的 N 号码搜索会把十六进制代码显示为 "Mode S Code (Base 16 / Hex)"。对于航空公司航班，呼号通常是航空公司的三字母代码加上航班号，这与机票上显示的不同：

| 机票 | 呼号 |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

有些航空公司发送的呼号不是航班号。如果某个航班没有出现，请在实时航班地图上查找它，并复制那里显示的呼号。呼号会被重复使用：明天的同一个呼号是另一次行程，也可能是另一架飞机。在你删除它之前，它会一直被跟踪。

**你会看到什么。** 每架被跟踪的飞机无论在哪里，都以它通常的图标和标签显示，即使你的区域已满。它的 `watch` 属性为 `followed`，`outside_radius` 表示它是否在你的圆圈外。在你的圆圈外，它每分钟移动一次；在圆圈内，和其他一切一样频繁。该区域的 `sensor.aircraft_in_range` 显示 `followed_asked`（你跟踪的代码数量）、`followed_found`（其中现在在空中的数量）和 `follow_status`（最近一次呼号请求的结果：`ok`，或出了什么问题）。

**要停止跟踪**，删除代码或清空该字段，然后选择 **提交**。

⚠ 只能找到发送 ADS-B 的飞机，或 MLAT 能够定位的飞机。在地面上或在接收机覆盖范围之外的飞机不会显示，`followed_found` 也不会统计它。这里不包括按航班号查询的时刻表和延误信息。

### 为某架飞机使用你自己的图片

用你选择的图片代替某架飞机的图标，例如你自己的飞机。

1. 在你的 Home Assistant 配置文件夹（包含 `configuration.yaml` 的文件夹）中，新建一个名为 `live_track_aircraft_pictures` 的文件夹。
2. 把图片放进去，以飞机的十六进制代码命名：`a1b2c3.png`。PNG、JPG、WebP、GIF 和 SVG 文件都可以，每个最大 2 MB。

图片会在一分钟内出现，更改或删除也一样。它是直立显示的，不会旋转，因为照片不是按机头朝上绘制的。这时飞机的 `picture_source` 属性为 `override`。

⚠ 这些图片和图标一样，无需登录即可访问：任何能通过地址访问你的 Home Assistant 的人都能打开它们。不要把私人图片放在那里。

### 美国总统的飞机

美国总统使用的飞机无论在世界的哪里都会显示，按它们的十六进制代码识别，从不按呼号识别，同时显示的还有第 89 空运联队的飞机（呼号 SAM 和 VENUS）和为总统飞机护航的军用飞机。它们来自 Live Track Aircraft 本来就会每分钟发出一次的请求。每架都带有一个 `watch` 属性，说明它为什么被显示，总统的飞机还在 `presidential_airframe` 中带有它的名称。

⚠ 地图上出现总统的飞机，并不说明机上有谁。

### EnforcementAircraft 列表与 Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft) 是一份移民和联邦执法机构所用飞机的公开列表，每个条目都附有来源，由 StrausbergAutomationWorks 发布。在你的区域内，列表根据来源确认的飞机会闪烁红色和蓝色，执飞 ICE Air 包机（以及其他业务）的客机带有持续的光晕。即使你的区域已满，它们也总是保留。

它的配套模块 [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) 会在列表中的飞机飞到任何地方时都画出它们，而不只是在你的区域内。两者都安装时，各自负责自己的部分：Live Track Aircraft 画出它自己区域内的每架飞机，包括列表中的飞机；Live Track SALT 画出其他所有地方的列表中的飞机。它们向来源共享同一个请求，没有飞机会被画两次。

---

## 它创建的全部实体

每个区域：

| 实体 | 是什么 |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**：现在圆圈内有多少架飞机，全部计算在内，即使超过上限。第二个区域的是 `sensor.aircraft_in_range_2`，依此类推 |
| `geo_location.aircraft_…` | 每架飞机一个，以它的十六进制代码命名（`geo_location.aircraft_a1b2c3`）；随飞机出现和消失。每个都带有 `source: live_track_aircraft`，它的状态是它与中心点的距离，单位为公里 |

传感器的属性说明正在发生什么：`published_count`（地图上有多少架）、`capped`（上限截断了列表时为 true）、`source`（最后响应的是哪个网络）、`source_backoff`、`route_artifact`、`route_download`、`airport_table`、`airport_download`、`route_lookup`、`watched_count`、`military_in_areas`、`military_by_area`、`followed_asked`、`followed_found`、`follow_status`、`adsblol_key` 和 `enforcement_list`。

⚠ **飞机标记故意没有唯一 ID。** 一个区域一年会看到成千上万架不同的飞机，为每架飞机在注册表中保留一行，只会白白让 Home Assistant 启动变慢。所以无法在界面中重命名、隐藏它们或为它们分配区域。它们的实体 ID 仍然来自十六进制代码，所以同一架飞机总是得到同一个 ID。传感器有唯一 ID，可以重命名。

⚠ **你的数据库。** Home Assistant 的记录器（recorder）在实体每次变化时都会存储一行新数据，而飞行中的飞机每次更新都会变化，默认每 15 秒一次。在我们的测试系统上，2026 年 9 月，一个这样每 15 秒更新一次的实体每天大约占用 9.6 MB；50 架飞机就是每天大约 480 MB。除非你想保留每架飞机的历史记录，否则请把它们排除在记录器之外。把下面的内容添加到 `configuration.yaml`，然后重启：

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

如果你的 `configuration.yaml` 已经有 `recorder:` 部分，只需在其中的 `exclude:` 和 `entity_globs:` 下添加 `geo_location.aircraft_*` 这一模式。这样，设置为绘制历史的地图卡片就没有轨迹可画了。`sensor.aircraft_in_range` 保留下来开销很小：它的属性取值很少，所以记录器只存储一次。

---

## 它发送和下载的内容

**关于你的位置。** 每个区域的中心点和半径会在每次更新时发送给 adsb.fi，默认每 15 秒一次，adsb.fi 没有响应时发送给 adsb.lol。中心点按你设置的样子发送，而它从你的家开始：要停止发送你家的位置，把中心点移离你家（**配置** → **Centre**），或删除该区域。你关注的十六进制代码和呼号每分钟发送一次给 adsb.fi（或 adsb.lol），你的 adsb.lol 密钥只发送给 adsb.lol。当 FiledRoutesDB 没有你区域内航空公司航班的航线时，这些航班的呼号会发送给 adsbdb。除此之外，不会向任何地方发送关于你的任何信息。每个服务都能看到你的互联网地址，就像任何网站一样。

**发送多少。**

| 来源 | 内容和频率 | 出错后 |
|---|---|---|
| adsb.fi | 每次更新时你圆圈内的每架飞机（默认每 15 秒一次）；每分钟一个请求，用于按十六进制代码跟踪的飞机和总统的飞机；一个用于军用飞机列表；一个用于所有被跟踪的呼号，只在你跟踪了呼号时发送 | 改为询问 adsb.lol。以 HTTP 429 拒绝的来源会在它要求的时间内被跳过，或者跳过 1 分钟，每次加倍，最多 10 分钟 |
| adsb.lol | 同样的请求，只在 adsb.fi 没有响应时发送 | 同上 |
| adsbdb | FiledRoutesDB 没有航线的每个新航空公司呼号一个请求，间隔至少 1 秒；答复保留 30 天，"没有航线"保留 24 小时。答复只保存在内存中 | 15 分钟内不再询问；收到 HTTP 429 后所有请求暂停 15 分钟 |
| FiledRoutesDB，来自 GitHub | 每天一个小的校验和文件，在芝加哥时间（美国）14:00 之后；文件本身大约 4.6 MB，只在它有变化时下载 | 一小时后重试；你已有的副本在过期前继续使用 |
| AirportZones，来自 GitHub | 每天一个小的校验和文件；表格本身大约 4.8 MB，只在它有变化时下载 | 一小时后重试；你已有的副本继续使用 |
| EnforcementAircraft，来自 GitHub | 每小时一个小的校验和文件；列表本身很小，只在它有变化时下载 | 你已有的副本继续使用 |
| FAA 航空器登记册（美国） | 登记册，大约 73 MB，每 7 天一次，来自 `registry.faa.gov` | 第二天重试；你已有的副本继续使用 |

下载的文件与其他 Live Track 模块共享，所以无论你安装多少个模块，每个文件只下载一次。它们保存在 Home Assistant 的 `.storage` 文件夹中，名称以 `saw_` 开头。如果你删除了 Live Track Aircraft，而且没有其他 Live Track 模块使用它们，你可以手动删除它们。

---

## 帮助它成长

Live Track Aircraft 仍在成长。我们发现新的航线来源、数据来源和飞机信息就会添加，也想知道你接下来希望看到什么。

### 提出建议

缺少你的国家、机场或机型吗？有什么地方不对，或难以理解？用你觉得最方便的方式告诉我们：

* [**填写一份简短的表单**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=zh-Hans.yml)，使用中文。你需要一个免费的 GitHub 账户。
* **发送电子邮件**到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)。无需账户。

无论哪种方式，告诉我们以下内容会有帮助：

* 你希望看到什么，以及在世界上的什么地方；
* 数据发布地点的链接，如果你知道的话（开放数据页面、公开数据源、服务网站）：不是必需的，但会有帮助；
* 你的 Home Assistant 语言，如果问题出在措辞或翻译上。

用英语或你自己的语言书写都可以，哪种方便用哪种。

### 在我们的帮助下自己添加

如果你想自己添加什么，我们会帮你完成，从第一个问题到最终发布。开始时你不需要是开发者：

* **翻译。** 设置对话框中的文字是一个文本文件里的一小串短语。我们会告诉你是哪个文件、哪几行。
* **新的数据来源。** 告诉我们数据在哪里发布。我们可以一起写代码，或者帮你检查你写的代码。
* **在你所在的地方测试。** 安装它，查看地图上你所在的部分，告诉我们哪些正确、哪些不正确。
* **修正这份 README。** 如果某个步骤与你看到的不一致，告诉我们你看到了什么。

[**告诉我们你的想法**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=zh-Hans.yml)，或写信到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)，我们会回复接下来的步骤。

---

## 语言

这份 README：[English](README.md)、[Deutsch](README.de.md)、[Français](README.fr.md)、[Nederlands](README.nl.md)、**简体中文**、[Español](README.es.md)、[Italiano](README.it.md)、[Dansk](README.da.md)。每份翻译的 README 都是完整的。

设置对话框和选项目前只有英文，无论你的 Home Assistant 使用什么语言。如果你会说其他语言，可以自己翻译它们：只是一个文件里的一小串短语，[我们会帮你完成](#在我们的帮助下自己添加)。

发现翻译中的错误，或需要其他语言？请在 <https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues> 告诉我们，或者[在我们的帮助下翻译](#在我们的帮助下自己添加)。

---

## 致谢与许可

* **adsb.fi**（<https://adsb.fi>）：飞机位置，开放数据，仅限个人非商业用途，遵守其[开放数据 README](https://github.com/adsbfi/opendata) 中的条款，条款要求注明 adsb.fi 并链接到它的主页。安装这个集成即表示你在使用 adsb.fi，它的条款适用于你。
* **adsb.lol**（<https://adsb.lol>）：飞机位置，采用 [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/)。安装这个集成即表示你在使用 adsb.lol，它的条款适用于你。两个网络都由志愿者运营：如果可以，请用一台接收机向它们提供数据来支持它们。
* **FiledRoutesDB**（[StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)）：来自向 FAA（美国）提交的飞行计划的航线，数据采用 CC BY 4.0，发布前已应用 FAA 的 LADD 列表。
* **adsbdb**（<https://www.adsbdb.com>）：FiledRoutesDB 之外的航线。它的航线数据是 David Taylor（爱丁堡）和 Jim Mason（格拉斯哥）的成果，未经许可不得复制或重新发布，因此答复只保存在内存中，从不写入文件，每架显示 adsbdb 航线的飞机都会注明他们。
* **FAA 航空器登记册**（美国联邦航空管理局，Federal Aviation Administration）：在美国注册的飞机的所有者和运营者名称，美国政府的公开数据。FAA 在发布文件之前，会自行删除被要求保密的名称。
* **OurAirports**（<https://ourairports.com>），通过 [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones)：机场名称和位置，采用 ODbL 1.0；时区由 StrausbergAutomationWorks 添加。
* **EnforcementAircraft**（[StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)）：移民和联邦执法飞机的列表，采用 ODbL 1.0。
* **ADS-B Radar**（<https://adsb-radar.com>）：飞机图标，来自 Jos Nutbroek 的 [SVG 飞机图标集](https://adsb-radar.com/help/icons.html)，按照其条款使用，条款要求提供这个反向链接。这些图标不在本存储库的 MIT 许可范围内。部分图标由 StrausbergAutomationWorks 按图标集的风格绘制并捐赠给 ADS-B Radar，因此也适用其条款。这个集成提供的图标使用了新的填充和轮廓，按飞机类别缩放，并为部分螺旋桨和旋翼添加了动画。每处改动都列在 [ATTRIBUTION.md](ATTRIBUTION.md) 中。
* **地图卡片**是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，MIT，是 nathan-gs 的 [ha-map-card](https://github.com/nathan-gs/ha-map-card)（MIT）的副本。它的地图瓦片及其署名见它的 README。

这些组织都没有制作或认可这个集成。

**代码**：MIT，见 [LICENSE](LICENSE)。

**开发者须知：** 实体遵循 Live Track 共享地图约定，因此每个模块都能在一张地图上显示，无需模板传感器；位置通过 `custom_components/live_track_aircraft/sources/` 中的来源接口进入，因此可以添加其他数据源而不改动实体。测试用 `python -m unittest discover -s tests` 运行。

---

## 关键词

Home Assistant 飞机 · Home Assistant 航班跟踪 · ADS-B · ADS-B 地图 · 航班跟踪 · 飞机追踪 · 头顶的飞机 · MLAT · Mode S · 航线 · 军用飞机 · 空军一号 · Air Force One · 直升机 · aircraft · flight tracker · Flugzeuge · Flugverfolgung · avions · suivi des vols · vliegtuigen · vluchten volgen · aviones · seguimiento de vuelos · aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb · FiledRoutesDB · FAA 登记册 · OurAirports · ADS-B Radar · geo_location · 地图卡片 · Lovelace · HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks

---

**致敬。** StrausbergAutomationWorks 向这张地图上世界各地陆地和水域的原住民族致意，并向他们过去和现在的长老致敬。
