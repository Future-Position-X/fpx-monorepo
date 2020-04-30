<template>
  <v-data-table :headers="headers" :items="tableData" item-key="id" class="elevation-1">
    <template v-slot:body="{ items, headers }">
      <tbody>
        <tr v-for="(item,idx) in items" :key="idx">
          <td v-for="(header,key) in headers" :key="key">
            <v-edit-dialog
              :return-value.sync="item[header.value]"
              @save="save"
              @cancel="cancel"
              @open="open"
              @close="close"
              large
            >
              {{item[header.value]}}
              <template v-slot:input>
                <v-text-field v-model="item[header.value]" label="Edit" single-line></v-text-field>
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
  name: "Table",
  data() {
    return {
      headers: [
        {
          text: "id",
          value: "id"
        },
        {
          text: "name",
          value: "name"
        },
        {
          text: "age",
          value: "age"
        }
      ],
      tableData: [
        { id: 1, name: "John", age: "20" },
        { id: 2, name: "Jane", age: "24" },
        { id: 3, name: "Susan", age: "16" },
        { id: 4, name: "Chris", age: "55" },
        { id: 5, name: "Dan", age: "40" }
      ]
    };
  },
  methods: {
          save() {},
    cancel() {},
    open() {},
    close() {}
  }
};
</script>