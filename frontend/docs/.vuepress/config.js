import { viteBundler } from '@vuepress/bundler-vite'
import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'

export default defineUserConfig({
  bundler: viteBundler(),
  theme: defaultTheme(),

  lang: 'fr-FR',
  title: 'Salut VuePress',
  description: 'Quelques tests pour documenter mon projet Vue 3'
})
