import { config } from '@vue/test-utils'

// Ensure vitest's expect is available before loading jest-dom matchers
// Use dynamic import so we can set the global before jest-dom runs
const { expect: vitestExpect } = await import('vitest')
globalThis.expect = vitestExpect
await import('@testing-library/jest-dom')

// Stubs for third-party UI components used in templates (FontAwesome)
// This prevents warnings like "Failed to resolve component: font-awesome-icon"
config.global.components = config.global.components || {}
config.global.components['font-awesome-icon'] = {
  name: 'FontAwesomeIconStub',
  template: '<svg aria-hidden="true"><slot/></svg>'
}
