<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
    <template #body-title>
      <div class="flex items-center gap-2 text-2xl font-semibold">
        {{ __('Edit Lead Qualification Layout') }}
        <Badge
          v-if="dirty"
          label="Not saved"
          theme="orange"
          variant="subtle"
        />
      </div>
    </template>

    <template #body-content>
      <div class="flex flex-col gap-3">
        <div class="flex justify-between">
          <Button
            :label="preview ? 'Hide preview' : 'Show preview'"
            @click="preview = !preview"
          />
          <div class="flex gap-2">
            <Button
              variant="solid"
              :loading="loading"
              label="Save"
              @click="save"
            />
            <Button label="Reset" @click="reload" />
          </div>
        </div>

        <FieldLayoutEditor
          v-if="tabs.data && !preview"
          :tabs="tabs.data"
          doctype="Lead Qualification"
        />
        <FieldLayout
          v-else-if="preview"
          :tabs="tabs.data"
          :data="{}"
          :preview="true"
          doctype="Lead Qualification"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Dialog, Badge, Button, call, createResource } from 'frappe-ui'

import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import FieldLayoutEditor from '@/components/FieldLayoutEditor.vue'

const show = defineModel()
const emit = defineEmits(['reload'])

const props = defineProps({
  doctype: String,
})

const preview = ref(false)
const loading = ref(false)
const dirty = ref(false)

/* --------------------------------------------------------------------------
   1. Tabs Resource
-------------------------------------------------------------------------- */

const tabParams = {
  doctype: props.doctype,
  type: 'Data Fields',
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  params: tabParams,
  auto: true,
  onSuccess(data) {
    tabs.originalData = JSON.parse(JSON.stringify(data))
    dirty.value = false // reset dirty state on fresh load
  },
})

/* --------------------------------------------------------------------------
   2. Dirty Tracking — guarded so it doesn't fire before originalData is set
-------------------------------------------------------------------------- */

watch(
  () => tabs.data,
  () => {
    if (!tabs.originalData) return
    dirty.value =
      JSON.stringify(tabs.data) !== JSON.stringify(tabs.originalData)
  },
  { deep: true }
)

/* --------------------------------------------------------------------------
   3. Actions
-------------------------------------------------------------------------- */

function reload() {
  tabs.params = tabParams
  tabs.reload()
}

function save() {
  const payload = JSON.parse(JSON.stringify(tabs.data))

  payload.forEach((tab) => {
    tab.sections?.forEach((section) => {
      section.columns?.forEach((column) => {
        column.fields = column.fields?.map((f) => f.fieldname || f.name)
      })
    })
  })

  loading.value = true

  call(
    'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.save_fields_layout',
    {
      doctype: props.doctype,
      type: 'Data Fields',
      layout: JSON.stringify(payload),
    }
  )
    .then(() => {
      loading.value = false
      show.value = false
      emit('reload')
    })
    .catch(() => {
      loading.value = false
      // Optionally add an error toast here
    })
}
</script>