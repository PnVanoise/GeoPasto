import en from '@vueform/vueform/locales/en'
import theme from '@vueform/vueform/dist/vueform'
// import vueform from '@vueform/vueform/themes/vueform'
import { defineConfig } from '@vueform/vueform'

export default defineConfig({
  theme,
  locales: { en },
  locale: 'en',
})