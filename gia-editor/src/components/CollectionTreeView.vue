<script>
import {VTreeview} from "vuetify/lib"
import CollectionTreeViewNode from "./CollectionTreeViewNode.vue";

export default {
  extends: VTreeview,
  render (h) {
    const children = this.items.length
        ? this.items.map(CollectionTreeViewNode.methods.genChild.bind(this))
        : this.$slots.default

    return h('div', {
      staticClass: 'v-treeview',
      class: {
        'v-treeview--hoverable': this.hoverable,
        'v-treeview--dense': this.dense,
        ...this.themeClasses,
      },
    }, children)
  },
}
</script>