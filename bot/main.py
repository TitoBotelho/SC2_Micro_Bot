from typing import Optional
from ares.consts import UnitRole, UnitTreeQueryType, ALL_STRUCTURES, WORKER_TYPES
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from cython_extensions import cy_closest_to, cy_in_attack_range, cy_pick_enemy_target
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
    ShootTargetInRange,
    AttackTarget,
    KeepUnitSafe,
)
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.data import Race

import time # for debug tool

import numpy as np


COMMON_UNIT_IGNORE_TYPES: set[UnitTypeId] = {
    UnitTypeId.EGG,
    UnitTypeId.LARVA,
    UnitTypeId.CREEPTUMORBURROWED,
    UnitTypeId.CREEPTUMORQUEEN,
    UnitTypeId.CREEPTUMOR,
    UnitTypeId.MULE,
}

class MyBot(AresBot):

    combat_manager = None
    ZERG_UNIT_TYPE: set[UnitTypeId] = { UnitTypeId.ZERGLING, UnitTypeId.ROACH }

    last_debug_time = 0 # Debug tool
    


    def __init__(self, game_step_override: Optional[int] = None):
        """Initiate custom bot

        Parameters
        ----------
        game_step_override :
            If provided, set the game_step to this value regardless of how it was
            specified elsewhere
        """
        super().__init__(game_step_override)




    async def on_start(self):
        
        await super().on_start()
        print("Game started")
        self.chat_send("teste 123")
        #self.enemy_initial_position = self.enemy_units[0].tag.position

        #TO DO: Implement a function to get the initial position based on the enemy start point


#_______________________________________________________________________________________________________________________
#          ON STEP
#_______________________________________________________________________________________________________________________



    async def on_step(self, iteration: int) -> None:
        await super(MyBot, self).on_step(iteration)

        # define targets and grid
        enemy_units = self.enemy_units
        ground_grid = self.mediator.get_ground_grid
        attack_target = None

        self.zergling_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_ONE)
        self.roach_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_TWO)
        queen_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_THREE)
        drone_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_FOUR)
        baneling_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_FIVE)



        await self.debug_tool()

        if enemy_units:
            target = enemy_units[0].position
        else:
            target = self.game_info.map_center


        if self.roach_squad:
            self.roach_army_attack(self.roach_squad, target, ground_grid)


        if self.zergling_squad:
            self.zergling_army_attack(self.zergling_squad, target, ground_grid)    



        #for unit in self.units(UnitTypeId.ROACH):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            #self.register_behavior(AMove(unit, target))

        for unit in self.units(UnitTypeId.QUEEN):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))


        for unit in self.units(UnitTypeId.DRONE):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))



        for unit in self.units(UnitTypeId.BANELING):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))

        for unit in self.units(UnitTypeId.RAVAGER):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))




        #for Unit in main_attack_force:
        #    main_maneuver = CombatManeuver()
        #    main_maneuver.add(AttackTarget(Unit, target))
            #main_maneuver.add(AMove(unit=Unit, target=target))
            #self.register_behavior(AMove(unit, self.game_info.map_center))


        # step logic here ...
        pass


#_______________________________________________________________________________________________________________________
#          ON UNIT CREATED
#_______________________________________________________________________________________________________________________



    async def on_unit_created(self, unit: Unit) -> None:
        await super(MyBot, self).on_unit_created(unit)

        if unit.type_id == UnitTypeId.ROACH:
            print("roach")

        if unit.type_id == UnitTypeId.ZERGLING:
            print("zergling")




        if unit.type_id == UnitTypeId.ZERGLING:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_ONE
            )

        if unit.type_id == UnitTypeId.ROACH:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_TWO
            )


        if unit.type_id == UnitTypeId.QUEEN:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_THREE
            )



        if unit.type_id == UnitTypeId.DRONE:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_FOUR
            )


        if unit.type_id == UnitTypeId.BANELING:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_FIVE
            )


        if unit.type_id == UnitTypeId.RAVAGER:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_SIX
            )







#_______________________________________________________________________________________________________________________
#          DEBUG TOOL
#_______________________________________________________________________________________________________________________

    async def debug_tool(self):
        current_time = time.time()
        if current_time - self.last_debug_time >= 1:  # Se passou mais de um segundo
            #print(self.mediator.get_all_enemy)
            #print("Enemy Race: ", self.EnemyRace)
            #print("Second Base: ", self.second_base)
            #print("Enemy Strategy: ", self.enemy_strategy)
            #print("Creep Queens: ", self.creep_queen_tags)
            #print("Creep Queen Policy: ", self.creep_queen_policy)
            #print("RallyPointSet: ", self.rally_point_set)
            #print("Enemy Structures: ", self.enemy_structures)
            print("Enemy Units: ", self.enemy_units)
            print("Unit Roles: ", self.mediator.get_unit_role_dict)
            print("zergling_squad: ", self.zergling_squad)
            #print("Enemy initial position: ", self.enemy_initial_position)
            #print("FirstBase: ", self.first_base)
            #print("SecondBase: ", self.second_base)
            self.last_debug_time = current_time  # Atualizar a última vez que a ferramenta de debug foi chamada


#_______________________________________________________________________________________________________________________
#          COMBAT MANEUVER
#_______________________________________________________________________________________________________________________


    def zergling_army_attack(self, main_attack_force: Units, attack_target: Point2, ground_grid: np.ndarray) -> None:    
        for unit in main_attack_force:
            if unit.is_idle:  # Verifica se a unidade está ociosa antes de dar o comando
                main_maneuver = CombatManeuver()
                main_maneuver.add(AMove(unit, attack_target))
                self.register_behavior(main_maneuver)


    def roach_army_attack(self, main_attack_force: Units, attack_target: Point2, ground_grid: np.ndarray) -> None:
        
        query_type: UnitTreeQueryType = (
            UnitTreeQueryType.EnemyGround
            if self.race == Race.Zerg
            else UnitTreeQueryType.AllEnemy
        )
        near_enemy: dict[int, Units] = self.mediator.get_units_in_range(
            start_points=main_attack_force,
            distances=15,
            query_tree=query_type,
            return_as_dict=True,
        )

        # get a ground grid to path on, this already contains enemy influence
        grid: np.ndarray = self.mediator.get_ground_grid

        # make a single call to self.attack_target property
        # otherwise it keep calculating for every unit
        target: Point2 = attack_target

        # use `ares-sc2` combat maneuver system
        # https://aressc2.github.io/ares-sc2/api_reference/behaviors/combat_behaviors.html
        for unit in main_attack_force:
            """
            Set up a new CombatManeuver, idea here is to orchestrate your micro
            by stacking behaviors in order of priority. If a behavior executes
            then all other behaviors will be ignored for this step.
            """

            attacking_maneuver: CombatManeuver = CombatManeuver()
            # we already calculated close enemies, use unit tag to retrieve them
            all_close: Units = near_enemy[unit.tag].filter(
                lambda u: not u.is_memory and u.type_id not in COMMON_UNIT_IGNORE_TYPES
            )
            only_enemy_units: Units = all_close.filter(
                lambda u: u.type_id not in ALL_STRUCTURES
            )

            # enemy around, engagement control
            if all_close:
                # ares's cython version of `cy_in_attack_range` is approximately 4
                # times speedup vs burnysc2's `all_close.in_attack_range_of`

                # idea here is to attack anything in range if weapon is ready
                # check for enemy units first
                if in_attack_range := cy_in_attack_range(unit, only_enemy_units):
                    # `ShootTargetInRange` will check weapon is ready
                    # otherwise it will not execute
                    attacking_maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )
                # then enemy structures
                elif in_attack_range := cy_in_attack_range(unit, all_close):
                    attacking_maneuver.add(
                        ShootTargetInRange(unit=unit, targets=in_attack_range)
                    )

                enemy_target: Unit = cy_pick_enemy_target(all_close)


                # low shield, keep protoss units safe
                if self.race == Race.Protoss and unit.shield_percentage < 0.3:
                    attacking_maneuver.add(KeepUnitSafe(unit=unit, grid=grid))

                else:
                    attacking_maneuver.add(
                        StutterUnitBack(unit=unit, target=enemy_target, grid=grid)
                    )

            # no enemy around, path to the attack target
            else:
                attacking_maneuver.add(AMove(unit=unit, target=target))

            # DON'T FORGET TO REGISTER OUR COMBAT MANEUVER!!
            self.register_behavior(attacking_maneuver)



    """
    Can use `python-sc2` hooks as usual, but make a call the inherited method in the superclass
    Examples:
    """
    # async def on_start(self) -> None:
    #     await super(MyBot, self).on_start()
    #
    #     # on_start logic here ...
    #
    # async def on_end(self, game_result: Result) -> None:
    #     await super(MyBot, self).on_end(game_result)
    #
    #     # custom on_end logic here ...
    #
    # async def on_building_construction_complete(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_building_construction_complete(unit)
    #
    #     # custom on_building_construction_complete logic here ...
    #
    # async def on_unit_created(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_unit_created(unit)
    #
    #     # custom on_unit_created logic here ...
    #
    # async def on_unit_destroyed(self, unit_tag: int) -> None:
    #     await super(MyBot, self).on_unit_destroyed(unit_tag)
    #
    #     # custom on_unit_destroyed logic here ...
    #
    # async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
    #     await super(MyBot, self).on_unit_took_damage(unit, amount_damage_taken)
    #
    #     # custom on_unit_took_damage logic here ...