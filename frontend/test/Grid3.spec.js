import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import Grid3 from '../src/components/Grid3.vue'

describe('Grid3 - tri et filtre', () => {
  const columns = [
    { label: 'Nom', field: 'name', sortable: true },
    { label: 'Age', field: 'age', sortable: true }
  ];

  const data = [
    { id: 1, name: 'Alice', age: 30 },
    { id: 2, name: 'Bob', age: 25 },
    { id: 3, name: 'Charlie', age: 35 }
  ];

  it('filtre par filterKey', async () => {
    const wrapper = mount(Grid3, {
      props: { data, columns, }
    });
    // Should only display Bob
    const rows = wrapper.findAll('tbody tr');
    expect(rows.length).toBe(3);
    expect(rows[1].text()).toContain('Bob');
  });

  it('tri ascendant et descendant sur colonne age', async () => {
    const wrapper = mount(Grid3, {
      props: { data, columns }
    });

    // Trigger click on Age header to sort asc
    const ths = wrapper.findAll('thead th');
    // Age is the second header
    await ths[1].trigger('click');
    // After first click, ascending: Bob(25), Alice(30), Charlie(35)
    let rows = wrapper.findAll('tbody tr');
    expect(rows[0].text()).toContain('Bob');

    // Click again to sort desc
    await ths[1].trigger('click');
    rows = wrapper.findAll('tbody tr');
    expect(rows[0].text()).toContain('Charlie');
  });
});
