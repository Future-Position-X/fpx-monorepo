import { mount } from '@vue/test-utils';
import Vue from 'vue';
import Vuetify from 'vuetify';

import Tree from './Tree.vue';

Vue.use(Vuetify);

const providerCache = {
  "677c6efd-5a6b-4201-b247-e1068c0376fc": {
    uuid: "677c6efd-5a6b-4201-b247-e1068c0376fc",
    name: "fpx"
  }
};

const sortedCollections = {
  __test: [
    {
      uuid: 'daa0c041-e720-48ee-bd73-657c6ef55d25',
      provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
      name: '__test',
      is_public: true,
      revision: 1,
      created_at: '2020-06-23 07:03:06.926628',
      updated_at: '2020-06-23 07:03:06.926628',
      color: 'hsl(7.5,100%,50%)',
      id: 'daa0c041-e720-48ee-bd73-657c6ef55d25',
      editable: true,
    },
  ],
  gg: [
    {
      uuid: '00000000-0000-0000-0000-000000000000',
      provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
      name: 'gg',
      is_public: true,
      revision: 0,
      created_at: '2020-05-07 13:07:23.126129',
      updated_at: '2020-05-07 13:07:23.126129',
      color: 'hsl(0,100%,50%)',
      id: '00000000-0000-0000-0000-000000000000',
      editable: true,
    },
  ],
};
const items = [
  {
    id: 'Owned collections',
    name: 'Owned collections',
    color: '#FFF',
    editable: false,
    children: [],
  },
  {
    id: 'Other collections',
    name: 'Other collections',
    color: '#FFF',
    editable: false,
    children: [
      {
        id: '__test',
        name: '__test',
        color: '#FFF',
        provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
        editable: false,
        children: [
          {
            uuid: 'daa0c041-e720-48ee-bd73-657c6ef55d25',
            provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
            name: '__test (fpx)',
            is_public: true,
            revision: 1,
            created_at: '2020-06-23 07:03:06.926628',
            updated_at: '2020-06-23 07:03:06.926628',
            color: 'hsl(7.5,100%,50%)',
            id: 'daa0c041-e720-48ee-bd73-657c6ef55d25',
            editable: true,
          },
        ],
      },
      {
        id: 'gg',
        name: 'gg',
        color: '#FFF',
        provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
        editable: false,
        children: [
          {
            uuid: '00000000-0000-0000-0000-000000000000',
            provider_uuid: '677c6efd-5a6b-4201-b247-e1068c0376fc',
            name: 'gg (fpx)',
            is_public: true,
            revision: 0,
            created_at: '2020-05-07 13:07:23.126129',
            updated_at: '2020-05-07 13:07:23.126129',
            color: 'hsl(0,100%,50%)',
            id: '00000000-0000-0000-0000-000000000000',
            editable: true,
          },
        ],
      },
    ],
  },
];

describe('Tree', () => {
  describe('data', () => {
    it('should render no elements when tree is empty', async () => {
      const wrapper = mount(Tree);
      expect(wrapper.element).toMatchSnapshot();
    });

    it('should render "owned" and "other" root elems when tree has items', async () => {
      const wrapper = mount(Tree);
      await wrapper.setData({ providerCache });
      await wrapper.setProps({ sortedCollections });
      expect(wrapper.vm.items).toMatchObject(items);
      expect(wrapper.element).toMatchSnapshot();
    });

    it('should render child items when opened', async () => {
      const wrapper = mount(Tree);
      await wrapper.setData({ providerCache });
      await wrapper.setProps({ sortedCollections });
      await wrapper.findComponent({ name: 'v-treeview' }).vm.updateOpen('Owned collections', false);
      await wrapper.findComponent({ name: 'v-treeview' }).vm.updateOpen('Other collections', true);
      expect(wrapper.text()).toContain('__test');
      expect(wrapper.text()).toContain('gg');
      expect(wrapper.element).toMatchSnapshot();
    });

    it('should render $checkboxOn when item is selected', async () => {
      const wrapper = mount(Tree);
      await wrapper.setData({ providerCache });
      await wrapper.setProps({ sortedCollections });
      const treeview = await wrapper.findComponent({ name: 'v-treeview' }).vm;
      await treeview.updateOpen('Owned collections', false);
      await treeview.updateOpen('Other collections', true);
      await treeview.updateOpen('__test', true);
      await treeview.updateSelected('daa0c041-e720-48ee-bd73-657c6ef55d25', true);
      expect(wrapper.text()).toContain('$checkboxOn__test (fpx)$subgroupgg');
      expect(wrapper.element).toMatchSnapshot();
    });
  });

  describe('selectionUpdate event', () => {
    it('should not include collections without uuids', async () => {
      // If "Owned collections" is empty and selected then it is emitted from v-treeview
      const wrapper = mount(Tree);
      await wrapper.setProps({ sortedCollections });
      await wrapper.findComponent({ name: 'v-treeview' }).vm.$emit('input', [items[0]]);
      const selectionUpdateEvents = wrapper.emitted('selectionUpdate');
      const firstEvent = selectionUpdateEvents[0];
      const firstArgument = firstEvent[0];
      expect(firstArgument).toEqual([]);
    });

    it('should include collections with uuids', async () => {
      const wrapper = mount(Tree);
      await wrapper.setProps({ sortedCollections });
      await wrapper
        .findComponent({ name: 'v-treeview' })
        .vm.$emit('input', Object.values(sortedCollections).flat());
      const selectionUpdateEvents = wrapper.emitted('selectionUpdate');
      const firstEvent = selectionUpdateEvents[0];
      const firstArgument = firstEvent[0];
      expect(firstArgument).toEqual([
        'daa0c041-e720-48ee-bd73-657c6ef55d25',
        '00000000-0000-0000-0000-000000000000',
      ]);
    });
  });
});
