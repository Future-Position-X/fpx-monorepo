<template>
  <v-data-table :headers="headers" :items="items" item-key="id" class="elevation-1" height="calc(100vh - 220px)">
    <template v-slot:body="{ items, headers }">
      <tbody>
        <tr v-for="(item, idx) in items" :key="idx">
          <td>{{ item.id }}</td>
          <td v-for="(header, key) in headers" :key="key">
            <v-edit-dialog
              :return-value.sync="item.properties[header.value]"
              @save="save"
              @cancel="cancel"
              @open="open"
              @close="close"
              large
            >
              {{ item.properties[header.value] }}
              <template v-slot:input>
                <v-text-field v-model="item.properties[header.value]" label="Edit" single-line></v-text-field>
              </template>
            </v-edit-dialog>
          </td>
        </tr>
      </tbody>
    </template>
  </v-data-table>
</template>
<script>
export default {
  name: 'Table',
  props: ['afc'],
  data() {
    return {
      items: this.afc ? this.afc.features : [],
    };
  },
  watch: {
    afc: {
      handler(val) {
        console.error("afc", val)
        if(val) {
          this.items = val.features;
        } else {
          this.items = [];
        }
      },
      deep: true
    }
  },
  computed: {
    headers() {
      console.debug("headers");
      const keys = this.items.reduce((acc, i) => {
        Object.keys(i.properties).forEach((key)=>acc.add(key));
        return acc;
      }, new Set());
      return ['id', ...keys].map((key) => { return {text: key, value: key}});
    }
  },
  methods: {
    save() {},
    cancel() {},
    open() {},
    close() {},
  },
};
</script>
