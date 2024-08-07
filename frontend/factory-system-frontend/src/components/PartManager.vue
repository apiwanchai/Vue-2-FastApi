<template>
  <div>
    <v-toolbar flat >
      <v-toolbar-title>Parts Changeover Matrix</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn class="mr-2" color="primary" @click="addRow">Add Part</v-btn>
      <v-btn  class="mr-2" color="secondary" @click="downloadExcel">Download Excel</v-btn>
      <input type="file" @change="handleFileUpload" style="display: none;" ref="fileInput">
      <v-btn class="mr-2" color="secondary" @click="triggerFileInput">Upload Excel</v-btn>
    </v-toolbar>

    <v-data-table
      :headers="headers"
      :items="parts"
      item-value="part_no"
      class="elevation-1"
    >
      <template v-slot:[`item.actions`]="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
        <v-icon small @click="deleteItem(item.part_no)">mdi-delete</v-icon>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="500px" @click:outside="close">
      <v-card>
        <v-card-title>
          <span class="headline">{{ formTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4" v-for="(value, key) in editedItem" :key="key">
                <v-text-field v-model="editedItem[key]" :label="key"></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog>
      <v-card>
        <v-card-title>
          <span class="headline">{{  checkRes === true ? "Success" : "errorr" }}</span>
        </v-card-title>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';


export default {
  setup() {
    const headers = [
      { text: 'Part No', value: 'part_no' },
      { text: 'TG1111', value: 'tg11111' },
      { text: 'TG2222', value: 'tg22222' },
      { text: 'TG3333', value: 'tg33333' },
      { text: 'TG4444', value: 'tg44444' },
      { text: 'TG5555', value: 'tg55555' },
      { text: 'TG6666', value: 'tg66666' },
      { text: 'Actions', value: 'actions', sortable: false }
    ];

    const parts = ref([]);
    const dialog = ref(false);
    const checkRes = ref(false)
    const editedItem = ref({
      part_no: '',
      tg1111: 0,
      tg2222: 0,
      tg3333: 0,
      tg4444: 0,
      tg5555: 0,
      tg6666: 0
    });
    const defaultItem = {
      part_no: '',
      tg1111: 0,
      tg2222: 0,
      tg3333: 0,
      tg4444: 0,
      tg5555: 0,
      tg6666: 0
    };

    const fetchData = () => {
      axios.get('http://127.0.0.1:8000/parts').then(response => {
        parts.value = response.data;
      });
    };

    const addRow = () => {
      editedItem.value = { ...defaultItem };
      dialog.value = true;
    };

    const editItem = (item) => {
      editedItem.value = { ...item };
      dialog.value = true;
    };

    const deleteItem = (part_no) => {
      console.log(part_no);
      axios.delete(`http://127.0.0.1:8000/delete-part/${part_no}`).then(() => {
        fetchData();
      });
    };

    const save = () => {
      if (editedItem.value.part_no) {
        axios.put(`http://127.0.0.1:8000/update-part/${editedItem.value.part_no}`, editedItem.value).then(() => {
          fetchData();
        });
      } else {
        axios.post('http://127.0.0.1:8000/add-part/', editedItem.value).then(() => {
          fetchData();
        });
      }
      close();
    };

    const close = () => {
      dialog.value = false;
      editedItem.value = { ...defaultItem };
    };

    const triggerFileInput = () => {
      fileInput.value.click();
    };

    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      axios.post('http://127.0.0.1:8000/import-excel/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(() => {
        fetchData();
      });
    };

    const downloadExcel = () => {
      axios.get('http://127.0.0.1:8000/export-excel/', {
        responseType: 'blob'
      }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'parts_changeover_matrix.xlsx');
        document.body.appendChild(link);
        link.click();
      });
    };

    onMounted(fetchData);

    const formTitle = computed(() => {
      return editedItem.value.part_no === '' ? 'New Item' : 'Edit Item';
    });

    const fileInput = ref(null);

    return {
      headers,
      parts,
      dialog,
      editedItem,
      formTitle,
      addRow,
      editItem,
      deleteItem,
      save,
      close,
      triggerFileInput,
      handleFileUpload,
      downloadExcel,
      fileInput
    };
  }
};
</script>

<style scoped>
.headline {
  font-weight: 400;
}
</style>
