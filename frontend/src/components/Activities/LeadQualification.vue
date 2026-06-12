<template>
  <div class="my-3 flex items-center justify-between text-lg font-medium sm:mb-4 sm:mt-8">
    <div class="flex h-8 items-center text-xl font-semibold text-ink-gray-8">
      {{ __('Lead Qualification') }}

      <Badge
        v-if="leadDoc?.isDirty"
        class="ml-3"
        label="Not Saved"
        theme="orange"
      />
    </div>

    <div class="flex gap-2">
      <Button
        v-if="docname && isManager()"
        label="Edit Layout"
        @click="showModal = true"
      />

      <Button
        v-if="docname"
        label="Save"
        :disabled="!leadDoc?.isDirty"
        variant="solid"
        :loading="leadDoc?.save?.loading"
        @click="saveChanges"
      />
    </div>
  </div>

  <div
    v-if="qualification.loading || (docname && (!leadDoc || leadDoc.loading))"
    class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-ink-gray-6"
  >
    <LoadingIndicator class="h-6 w-6" />
    <span>{{ __('Loading...') }}</span>
  </div>

  <div
    v-else-if="!docname"
    class="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center text-xl font-medium text-ink-gray-6"
  >
    <p>{{ __('No Lead Qualification found for this lead.') }}</p>
    <Button
      label="Create Qualification"
      variant="solid"
      @click="createNewQualification"
    />
  </div>

  <div v-else class="pb-8">
    <FieldLayout
      v-if="tabs.data && leadDoc?.doc"
      :tabs="filteredTabs"
      :data="leadDoc.doc"
      doctype="Lead Qualification"
    />
  </div>

  <LeadQualificationModal
    v-if="showModal"
    v-model="showModal"
    doctype="Lead Qualification"
    @reload="tabs.reload"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Badge, Button, createResource } from 'frappe-ui'

import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import LeadQualificationModal from '@/components/Modals/LeadQualificationModal.vue'

import { useDocument } from '@/data/document'
import { usersStore } from '@/stores/users'

const props = defineProps({
  leadId: {
    type: String,
    required: true,
  },
})

const { isManager } = usersStore()
const showModal = ref(false)
const docname = ref(null)
const leadDoc = ref(null)

/* --------------------------------------------------------------------------
   1. Resource Fetching
-------------------------------------------------------------------------- */

const qualification = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: 'Lead Qualification',
    filters: { lead: props.leadId },
    fieldname: ['name'],
  },
  auto: true,
})

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  params: {
    doctype: 'Lead Qualification',
    type: 'Data Fields',
  },
  auto: true,
})

/* --------------------------------------------------------------------------
   2. Document Resolution
-------------------------------------------------------------------------- */

// Sync docname from qualification resource
watch(
  () => qualification.data,
  (val) => {
    docname.value = val?.name || null
  },
  { immediate: true }
)

// Resolve useDocument only when docname is available — avoids calling
// composable inside computed (which would leak instances on every read)
watch(
  docname,
  (name) => {
    if (name) {
      leadDoc.value = useDocument('Lead Qualification', name).document
    } else {
      leadDoc.value = null
    }
  },
  { immediate: true }
)

// Dirty tracking — only runs once original doc is available
watch(
  () => leadDoc.value?.doc,
  (newVal, oldVal) => {
    if (!leadDoc.value || !oldVal || !newVal) return

    leadDoc.value.isDirty =
      JSON.stringify(newVal) !== JSON.stringify(leadDoc.value.originalDoc)
  },
  { deep: true }
)

/* --------------------------------------------------------------------------
   3. Computed Layout Filtering
-------------------------------------------------------------------------- */

const filteredTabs = computed(() => {
  if (!tabs.data) return []

  const cloned = JSON.parse(JSON.stringify(tabs.data))

  cloned.forEach((tab) => {
    tab.sections?.forEach((section) => {
      section.columns?.forEach((column) => {
        column.fields = column.fields?.filter((f) => f.fieldname !== 'lead')
      })
    })
  })

  return cloned
})

/* --------------------------------------------------------------------------
   4. Actions
-------------------------------------------------------------------------- */

// function saveChanges() {
//   if (!leadDoc.value?.isDirty) return
//   leadDoc.value.save.submit()
// }

const insertResource = createResource({
  url: 'frappe.client.insert',
  onSuccess() {
    qualification.reload()
    emit('reloadLead')
  },
})

const emit = defineEmits(['reloadLead'])

function saveChanges() {
  if (!leadDoc.value?.isDirty) return
  leadDoc.value.save.submit(null, {
    onSuccess() {
      emit('reloadLead')
    }
  })
}

function createNewQualification() {
  insertResource.submit({
    doc: {
      doctype: 'Lead Qualification',
      lead: props.leadId,
    },
  })
}
</script>