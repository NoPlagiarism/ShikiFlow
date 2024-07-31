# ShikiFlow

> Search anime/manga on [Shikimori](https://shikimori.one) with [Flow (Launcher)](https://www.flowlauncher.com)

## Installation

> pm install ShikiFlow

## Features

- Search Anime and\or Manga [available on Shikimori](https://shikimori.one/anime-industry)
- Open external links for selected media, if available
- Search Anime/Manga on your favorite websites
- Copy/See Russian, English, Japanese and other titles

## How-To

### Enable Russian Layout Support

`shk s:rus` -> Enter. And from this moment `ырл Дурочка` should work

### Change language

You can choose between Russian and English in plugin settings

### Search

- To search
  - Manga - use tag `m:` -> `shk m:Love is hard for otaku`
  - Anime - use tag `a:` -> `shk a:Nichijou`
  - Both - use tag `b:` -> `shk b:Horimiya`

You can choose default type of media in plugin settings

### Main language for title

Choose it in settings

### External Links

External Links are that kind of links, that Shikimori provides itself.

- To De/Select external link
  - Go to `shk s:extl`
  - Go to context menu (Press arrow right →)

### External Search

External Search opens search of selected Anime/Manga

- To search from [available list](https://github.com/NoPlagiarism/AnMaSearchTerms)
  - Go to `shk s:exts e`
  - Select needed site
  - Go to context menu (Press arrow right →)
- To delete
  - Go to `shk s:exts d`
  - Select item for delete
  - Go to context menu (Press arrow right →)

- Where this data coming from?
  - From [repository](https://github.com/NoPlagiarism/AnMaSearchTerms), and this repo contains some custom entries, but mostly data is taken from [MAL-Sync](https://malsync.moe)

### How to add own external search

<!-- TODO: write this after AnMaSearchTerms ReadMe -->
<!-- - Go to `UserData` folder (`Flow Launcher UserData Folder` in Flow Launcher)
- Go to `Settings\Plugins\ShikiFlow`
- Open `osettings.json`
  - If it does not exists, try adding some External Link or External Search using steps above
- -->

Edit `osettings.json`

Also, you can try [opening issue in mentioned repo](https://github.com/NoPlagiarism/AnMaSearchTerms), but I cannot guarantee adding anything

### Replace icon of specific website

- Download .png icon
- Go to plugin settings folder
  - Go to `UserData` folder (`Flow Launcher UserData Folder` in Flow Launcher)
  - Go to `Settings\Plugins\ShikiFlow`
- Save icon in `Favs` folder with "`DOMAIN.png`" name
  - `www.hidive.com` -> `hidive.com.png`
  - `smotret-anime.com` -> `smotret-anime.com.png`
