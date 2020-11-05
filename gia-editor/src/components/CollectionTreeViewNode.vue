<script>
import {VTreeviewNode} from "vuetify/lib/components/VTreeview"
import {getObjectValueByPath} from "vuetify/lib/util/helpers";
import {VIcon} from "vuetify/lib/components/VIcon/index";

const CollectionTreeViewNode = {
  extends: VTreeviewNode,
  methods: {
    genChild (item) {
      return this.$createElement(CollectionTreeViewNode, {
        key: getObjectValueByPath(item, this.itemKey),
        props: {
          activatable: item.activatable,
          activeClass: this.activeClass,
          item,
          selectable: item.selectable,
          selectedColor: this.selectedColor,
          color: this.color,
          expandIcon: this.expandIcon,
          indeterminateIcon: this.indeterminateIcon,
          offIcon: this.offIcon,
          onIcon: this.onIcon,
          loadingIcon: this.loadingIcon,
          itemKey: this.itemKey,
          itemText: this.itemText,
          itemDisabled: this.itemDisabled,
          itemChildren: this.itemChildren,
          loadChildren: this.loadChildren,
          transition: this.transition,
          openOnClick: this.openOnClick,
          rounded: this.rounded,
          shaped: this.shaped,
          level: this.level + 1,
        },
        scopedSlots: this.$scopedSlots,
      })
    },
    genCheckbox () {
      return this.$createElement(VIcon, {
        staticClass: 'v-treeview-node__checkbox',
        props: {
          color: this.isSelected ? this.selectedColor : undefined,
        },
        on: {
          click: (e) => {
            if (this.disabled) return

            e.stopPropagation()

            if (this.isLoading) return

            this.checkChildren().then(() => {
              // We nextTick here so that items watch in VTreeview has a chance to run first
              this.$nextTick(() => {
                this.isSelected = !this.isSelected
                this.isIndeterminate = false

                this.treeview.updateSelected(this.key, this.isSelected)
                this.treeview.emitSelected()

                if(this.isSelected || (!this.isSelected && this.isActive)) {
                  this.isActive = this.isSelected
                  this.treeview.updateActive(this.key, this.isActive)
                  this.treeview.emitActive()
                }
              })
            })
          },
        },
      }, [this.computedIcon])
    },
    genNode () {
      const children = [this.genContent()]

      if (this.selectable) children.unshift(this.genCheckbox())

      if (this.hasChildren) {
        children.unshift(this.genToggle())
      } else {
        children.unshift(...this.genLevel(1))
      }

      children.unshift(...this.genLevel(this.level))

      return this.$createElement('div', this.setTextColor(this.isActive && this.color, {
        staticClass: 'v-treeview-node__root',
        class: {
          [this.activeClass]: this.isActive,
        },
        on: {
          click: () => {
            if (this.disabled) return

            if (this.openOnClick && this.hasChildren) {
              this.open()
            } else if (this.activatable && this.isSelected) {
              this.isActive = !this.isActive
              this.treeview.updateActive(this.key, this.isActive)
              this.treeview.emitActive()
            }
          },
        },
      }), children)
    },
  }
}
export default CollectionTreeViewNode;
</script>